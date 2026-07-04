import operator
from semantic_analizer import SemanticAnalizer
from parser import Parser, Node
from lexer import Lexer

class Optimizer:
    OPS_TABLE = {
        Lexer.PLUS: operator.add,
        Lexer.MINUS: operator.sub,
        Lexer.ASTERISK: operator.mul,
        Lexer.SLASH: operator.floordiv,
        Lexer.PERCENT: operator.mod,
        Lexer.DOUBLE_EQ: operator.eq,
        Lexer.NE: operator.ne,
        Lexer.LT: operator.lt,
        Lexer.LE: operator.le,
        Lexer.GT: operator.gt,
        Lexer.GE: operator.ge,
        Lexer.DOUBLE_AMPER: lambda a, b: a if not a else b,
        Lexer.DOUBLE_PIPE: lambda a, b: a if a else b
        }
    
    def __init__(self, text):
        self.analizer = SemanticAnalizer(text)

    def is_zero(self, node):
        if node.kind == Parser.NUM and node.value == 0:
            return True
        else:
            return False

    def is_one(self, node):
        if node.kind == Parser.NUM and node.value == 1:
            return True
        else:
            return False

    def fold_binop(self, node):
        left = node.childs[0]
        right = node.childs[1]
        
        if left.kind == right.kind == Parser.NUM:
            return Node(kind=Parser.NUM, value=Optimizer.OPS_TABLE[node.value](left, right))

        match node.value:
            case Lexer.PLUS:
                if self.is_zero(left):
                    return right
                if self.is_zero(right):
                    return left
            case Lexer.MINUS:
                if self.is_zero(left):
                    return Node(kind=Parser.UNARY, value=Lexer.MINUS, childs=[right])
                if self.is_zero(right):
                    return left
            case Lexer.ASTERISK:
                if self.is_zero(left) or is_zero(right):
                    return Node(kind=Parser.NUM, value=0)
                if self.is_one(left):
                    return right
                if self.is_one(right):
                    return left
            case Lexer.SLASH:
                if self.is_zero(left):
                    return Node(kind=Parser.NUM, value=0)
                if self.is_one(right):
                    return left
                if left.kind == right.kind == Parser.IDENT and \
                   left.value == right.value:
                    return Node(kind=Parser.NUM, value=1)
            case Lexer.PERCENT:
                if left.kind == right.kind == Parser.IDENT and \
                   left.value == right.value or self.is_one(right):
                    return Node(kind=Parser.NUM, value=0)

        return node

    def fold_unary(self, node):
        operand = node.childs[0]

        if operand.kind == Parser.UNARY and operand.value == node.value:
            return operand.childs[0]
        
        match node.value:
            case Lexer.MINUS:
                if operand.kind == Parser.NUM:
                    return Node(kind=Parser.NUM, value=-operand.value)
            case Lexer.EX_MARK:
                if operand.kind == Parser.NUM:
                    return Node(kind=Parser.NUM, value=not operand.value)

        return node

    def fold_if(self, node):
        if node.childs[0].kind == Parser.NUM:
            if cond.value != 0:
                return node.childs[1]
            else:
                if len(node.childs) > 2:
                    return node.childs[2]
                else:
                    return Node(kind=Parser.EMPTY)

        return node

    def fold_while(self, node):
        if node.childs[0].kind == Parser.NUM:
            if cond.value == 0:
                return Node(kind=Parser.EMPTY)

        return node

    def remove_dead_code(self, node):
        if not node.childs:
            return Node(kind=Parser.EMPTY)

        new_childs = []
        for n in node.childs:
            if n.kind == Parser.EMPTY:
                continue

            new_childs.append(n)

        node.childs = new_childs
        return node
         
    def optimize_ast(self):
        ast = self.analizer.analize_ast()

        self.optimize(ast)

        return ast

    def optimize(self, node):
        for i, n in enumerate(node.childs):
            node.childs[i] = self.optimize(n)

        match node.kind:
            case Parser.BINOP:
                return self.fold_binop(node)
            case Parser.UNARY:
                return self.fold_unary(node)
            case Parser.IF:
                return self.fold_if(node)
            case Parser.WHILE:
                return self.fold_while(node)
            case Parser.BLOCK:
                return self.remove_dead_code(node)
            case _:
                return node
