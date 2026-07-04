from parser import Parser, print_ast
from lexer import Lexer

class SemanticAnalizer:
    def __init__(self, text):
        self.parser = Parser(text)

        self.block_count = 1
        self.var_table = {0: []}

    def error(self, text):
        print('Semantic error:', text)
        exit(1)

    def analize_ast(self):
        ast = self.parser.parse()
        self.analize(ast)
        return ast

    def analize(self, node, block=0):
        match node.kind:
            case Parser.BINOP:
                match node.value:
                    case Lexer.SLASH:
                        if node.childs[1].kind == Parser.NUM and node.childs[1].value == 0:
                            self.error('Division by zero')

                        for n in node.childs:
                            self.analize(n, block)
                    case Lexer.EQ:
                        for n in node.childs[1:]:
                            self.analize(n, block)

                        self.var_table[block].append(node.childs[0].value)
                    case Lexer.GLOBAL:
                        for n in node.childs[1:]:
                            self.analize(n, block)

                        self.var_table[0].append(node.childs[0].value)
            case Parser.BLOCK:
                self.var_table[self.block_count] = []
                
                for n in node.childs:
                    self.analize(n, self.block_count)

                self.block_count += 1
            case Parser.FN_SIGNATURE:
                self.var_table[block].append(node.value)
                self.var_table[self.block_count] = []

                self.analize(node.childs[0], self.block_count)
                self.analize(node.childs[1], self.block_count)

                self.block_count += 1
            case Parser.PARAMS:
                for n in node.childs:
                    self.var_table[block].append(n.value)
            case Parser.USE:
                pass
            case Parser.IDENT:
                if node.value not in self.var_table[block] and \
                   node.value not in self.var_table[0]:
                    self.error(f'Variable {node.value} has not assigned')
            case _:
                for n in node.childs:
                    self.analize(n, block)
