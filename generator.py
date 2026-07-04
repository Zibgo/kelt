from lexer import Lexer
from parser import Parser, Node
from optimizer import Optimizer
from kvm import KVM

class Generator:

    BIN_OPS = {
        Lexer.DOUBLE_PIPE: '@or',
        Lexer.DOUBLE_AMPER: '@and',
        Lexer.DOUBLE_EQ: '@eq', Lexer.NE: '@ne', Lexer.LT: '@lt', Lexer.LE: '@le', Lexer.GT: '@gt', Lexer.GE: '@ge',
        Lexer.PLUS: '@add', Lexer.MINUS: '@sub',
        Lexer.ASTERISK: '@mul', Lexer.SLASH: '@fdiv', Lexer.PERCENT: '@mod'
        }

    UN_OPS = {
        Lexer.MINUS: '@neg',
        Lexer.EX_MARK: '@not'
        }

    def __init__(self, text):
        self.optimizer = Optimizer(text)
        self.code = []

        self.labels = {}

        self.if_count = 0
        self.loop_count = 0

    def code_append(self, label, op, arg=None):
        if label is None:
            self.code.append((op, arg))
        else:
            self.labels[label].append((op, arg))

    def generate_code(self):
        self.ast = self.optimizer.optimize_ast()
        self.generate_for_node(self.ast, None)
        for label_name in self.labels:
            self.code_append(None, KVM.LABEL, label_name)
            self.code += self.labels[label_name]
        return self.code

    def generate_for_node(self, node, label):
        match node.kind:
            case Parser.PROGRAM:
                self.code_append(label, KVM.USE, ('stdlib', ('std', )))
                self.code_append(label, KVM.USE, ('stdlib', ('std', 'logical')))
                
                for use_node in [n for n in node.childs if n.kind == Parser.USE]:
                    self.generate_for_node(use_node, label)

                for fn_node in [n for n in node.childs if n.kind == Parser.FN_SIGNATURE]:
                    self.generate_for_node(fn_node, label)

                self.code_append(label, KVM.JMP, 'main')
                self.code_append('main', KVM.HALT)
            case Parser.USE:
                self.code_append(label, KVM.USE, f'{node.childs[0].value}.kbc')
            case Parser.FN_SIGNATURE:
                self.labels[node.value] = []
                
                self.code_append(label, KVM.FN, node.value)
                self.code_append(label, KVM.STORE, node.value)

                self.generate_for_node(node.childs[0], node.value)
                self.generate_for_node(node.childs[1], node.value)

            case Parser.PARAMS:
                for i, n in enumerate(node.childs):
                    self.code_append(label, KVM.LOAD, f'-arg{i}')
                    self.code_append(label, KVM.STORE, n.value)

            case Parser.BLOCK:
                for n in node.childs:
                    self.generate_for_node(n, label)

            case Parser.EMPTY:
                pass
            case Parser.IF:
                self.generate_for_node(node.childs[0], label)
                
                self.code_append(label, KVM.JNZ, f'-endif{self.if_count}')
                if len(node.childs) == 3:
                    self.code_append(label, KVM.JZ, f'-else{self.if_count}')
                    
                    self.generate_for_node(node.childs[1], label)
                    
                    self.code_append(label, KVM.JMP, f'-endif{self.if_count}')
                    self.code_append(label, KVM.LABEL, f'-else{self.if_count}')

                    self.generate_for_node(node.childs[2], label)

                    self.code_append(label, KVM.LABEL, f'-endif{self.if_count}')
                else:
                    self.code_append(label, KVM.JZ, f'-endif{self.if_count}')

                    self.generate_for_node(node.childs[1], label)

                    self.code_append(label, KVM.LABEL, f'-endif{self.if_count}')

                self.if_count += 1
            case Parser.WHILE:
                self.code_append(label, KVM.LABEL, f'-loop{self.loop_count}')

                self.generate_for_node(node.childs[0], label)

                self.code_append(label, KVM.JZ, f'-endloop{self.loop_count}')

                self.generate_for_node(node.childs[1], label)

                self.code_append(label, KVM.JMP, f'-loop{self.loop_count}')
                self.code_append(label, KVM.LABEL, f'-endloop{self.loop_count}')

                self.loop_count += 1
            case Parser.RET:
                self.generate_for_node(node.childs[0], label)
                
                self.code_append(label, KVM.RET)
            case Parser.BINOP:
                match node.value:
                    case Lexer.EQ:
                        #print('f', node)
                        self.generate_for_node(node.childs[1], label)
                        self.code_append(label, KVM.STORE, node.childs[0].value)
                    case Lexer.GLOBAL:
                        self.generate_for_node(node.childs[1], label)
                        self.code_append(label, KVM.STOREG, node.childs[0].value)
                    case _:
                        self.generate_for_node(node.childs[0], label)
                        self.generate_for_node(node.childs[1], label)

                        self.code_append(label, KVM.LOAD, Generator.BIN_OPS[node.value])
                        self.code_append(label, KVM.CALL, 2)
            case Parser.UNARY:
                self.generate_for_node(node.childs[0], label)

                self.code_append(label, KVM.LOAD, Generator.UN_OPS[node.value])
                self.code_append(label, KVM.CALL, 1)
            case Parser.CALL:
                for arg in node.childs:
                    self.generate_for_node(arg, label)
                    
                self.code_append(label, KVM.LOAD, node.value)
                self.code_append(label, KVM.CALL, len(node.childs))
            case Parser.IDENT:
                self.code_append(label, KVM.LOAD, node.value)
            case Parser.NUM:
                self.code_append(label, KVM.PUSH, node.value)
