import sys
from dataclasses import dataclass, field
from lexer import Lexer
from typing import Any

@dataclass
class Node:
    kind: int | None = None
    value: Any = None
    childs: list[Node] = field(default_factory=list)


class Parser:

    OPS_PRECEDENCE = {
        Lexer.EQ: 1,
        Lexer.DOUBLE_PIPE: 2,
        Lexer.DOUBLE_AMPER: 3,
        Lexer.DOUBLE_EQ: 4, Lexer.NE: 4, Lexer.LT: 4, Lexer.LE: 4, Lexer.GT: 4, Lexer.GE: 4,
        Lexer.PLUS: 5, Lexer.MINUS: 5,
        Lexer.ASTERISK: 6, Lexer.SLASH: 6, Lexer.PERCENT: 6,
        }

    RIGHT_ASSOC = [Lexer.EQ]
    
    UNARY_OPS = [Lexer.MINUS, Lexer.EX_MARK]
    
    NUM, IDENT, PROGRAM, USE, FN_SIGNATURE, EMPTY, IF, \
    BLOCK, WHILE, RET, BINOP, \
    UNARY, CALL, PARAMS = range(14) #node kinds   
    
    def __init__(self, text):
        self.lexer = Lexer(text)

    def error(self, text):
        print(f'Parser error: {text} at line {self.token[2]}, column {self.token[3]}')
        input('Press any key to close this program')
        sys.exit(1)

    def get_token(self):
        self.token = self.lexer.get_token()

    def view_next_token(self):
        next_token = self.lexer.get_token()
        
        cursor_pos = self.lexer.stream.tell()
        self.lexer.stream.seek(cursor_pos - 1)

        self.lexer.ch = ' '

        return next_token

    def primary(self):
        n = Node()

        match self.token[0]:
            case Lexer.NUM:
                n.kind = Parser.NUM
                n.value = self.token[1]

                self.get_token()
            case Lexer.IDENT:
                n.value = self.token[1]

                self.get_token()

                if self.token[0] == Lexer.LSQR:
                    self.get_token()
                    args = []

                    if self.token[0] != Lexer.RSQR:
                        args.append(self.expression())

                        while self.token[0] == Lexer.COMMA:
                            self.get_token()

                            args.append(self.expression())
                        if self.token[0] != Lexer.RSQR:
                            self.error('"]" expected')
                        self.get_token()
                    else:
                        self.get_token()
                        
                    n.kind = Parser.CALL
                    n.childs = args
                else:
                    n.kind = Parser.IDENT
            case Lexer.LPAR:
                self.get_token()
                
                n = self.expression()

                if self.token[0] != Lexer.RPAR:
                    self.error('")" expected')
                self.get_token()
        return n
        
    def unary(self):
        if self.token[0] in Parser.UNARY_OPS:
            n = Node(kind=Parser.UNARY)

            n.value = self.token[0]
            self.get_token()

            n.childs.append(self.primary())

            return n
        else:
            return self.primary()

    def expression(self, min_prec=0):
        left = self.unary()

        while self.token[0] in Parser.OPS_PRECEDENCE:
            op = self.token[0]
            prec = Parser.OPS_PRECEDENCE[op]

            if prec < min_prec:
                break

            next_prec = prec if op in Parser.RIGHT_ASSOC else prec + 1
            self.get_token()

            right = self.expression(next_prec)

            left = Node(kind=Parser.BINOP, value=op, childs=[left, right])

        return left
            
    def global_assign(self):
        self.get_token()

        n = self.expression()

        if n.value != Lexer.EQ:
            self.error('Variable assignment after "global" keyword expected')

        n.value = Lexer.GLOBAL

        if self.token[0] != Lexer.SEMICOLON:
            self.error('";" expected')
            
        self.get_token()

        return n

    def ret_stmt(self):
        n = Node(kind=Parser.RET)

        self.get_token()

        n.childs.append(self.expression())

        if self.token[0] != Lexer.SEMICOLON:
            self.error('";" expected blad')

        self.get_token()

        return n

    def while_stmt(self):
        n = Node(kind=Parser.WHILE)

        self.get_token()

        n.childs.append(self.expression())
        n.childs.append(self.statement())

        return n

    def if_stmt(self):
        n = Node(kind=Parser.IF)

        self.get_token()

        n.childs.append(self.expression())
        n.childs.append(self.statement())

        if self.token[0] == Lexer.ELSE:
            n.childs.append(self.statement())

        return n

    def block(self):
        n = Node(kind=Parser.BLOCK)

        self.get_token()
        while self.token[0] != Lexer.RBRA:
            n.childs.append(self.statement())

        self.get_token()

        return n

    def empty_stmt(self):
        n = Node(kind=Parser.EMPTY)

        self.get_token()

        return n

    def statement(self):
        n = Node()

        match self.token[0]:
            case Lexer.SEMICOLON:
                n = self.empty_stmt()
            case Lexer.LBRA:
                n = self.block()
            case Lexer.FN:
                n = self.fn_signature()
            case Lexer.IF:
                n = self.if_stmt()
            case Lexer.WHILE:
                n = self.while_stmt()
            case Lexer.RET:
                n = self.ret_stmt()
            case Lexer.GLOBAL:
                n = self.global_assign()
            case Lexer.IDENT | Lexer.NUM | Lexer.LPAR | Lexer.MINUS | Lexer.EX_MARK:
                    n = self.expression()
                    
                    if self.token[0] != Lexer.SEMICOLON:
                        self.error('";" expected')
                    self.get_token()
        return n

    def fn_signature(self):
        n = Node(kind=Parser.FN_SIGNATURE)

        self.get_token()
        if self.token[0] != Lexer.IDENT:
            self.error('Function name expected')
        n.value = self.token[1]

        self.get_token()
        if self.token[0] != Lexer.LSQR:
            self.error('"[" expected')

        self.get_token()

        params = Node(Parser.PARAMS)
        
        while self.token[0] == Lexer.IDENT:
            params.childs.append(Node(kind=Parser.IDENT, value=self.token[1]))

            self.get_token()
            if self.token[0] == Lexer.COMMA:
                self.get_token()
        if self.token[0] != Lexer.RSQR:
            self.error('"]" expected')

        n.childs.append(params)

        self.get_token()
        n.childs.append(self.statement())
            
        return n

    def use_directive(self):
        n = Node(kind=Parser.USE)

        self.get_token()
        if self.token[0] != Lexer.IDENT:
            self.error('Package name expected')
        n.childs.append(Node(kind=Parser.IDENT, value=self.token[1]))

        self.get_token()
        if self.token[0] == Lexer.SEMICOLON:
            self.get_token()
            return n

        if self.token[0] != Lexer.COLON:
            self.error('":" or ";" expected')

        while self.token[0] != Lexer.SEMICOLON:
            if self.token[0] != Lexer.COLON:
                self.error('":" or ";" expected')

            self.get_token()

            if self.token[0] != Lexer.IDENT:
                self.error('Library name expected')
                
            n.childs.append(Node(kind=Parser.IDENT, value=self.token[1]))

        self.get_token()
        return n

    def parse(self):
        self.get_token()

        n = Node(kind=Parser.PROGRAM)

        if self.token[0] not in (Lexer.USE, Lexer.FN, Lexer.EOF):
            self.error("Unresolved keyword")
        while self.token[0] == Lexer.USE:
            n.childs.append(self.use_directive())
        if self.token[0] not in (Lexer.USE, Lexer.FN, Lexer.EOF):
            self.error("Unresolved keyword")
        while self.token[0] == Lexer.FN:
            n.childs.append(self.fn_signature())
        if self.token[0] != Lexer.EOF:
            self.error("Invalid syntax")

        return n

def print_ast(node, indent=0):
    nodes_table = {
        Parser.NUM: 'num',
        Parser.IDENT: 'ident',
        Parser.PROGRAM: 'program',
        Parser.USE: 'use',
        Parser.FN_SIGNATURE: 'fn_signature',
        Parser.EMPTY: 'empty',
        Parser.IF: 'if',
        Parser.BLOCK: 'block',
        Parser.WHILE: 'while',
        Parser.RET: 'ret',
        Parser.BINOP: 'binop',
        Parser.UNARY: 'unary',
        Parser.CALL: 'call',
        Parser.PARAMS: 'params'
        }

    ops_table = {
        Lexer.EQ: 'eq',
        Lexer.DOUBLE_PIPE: 'logic_or',
        Lexer.DOUBLE_AMPER: 'logic_and',
        Lexer.DOUBLE_EQ: 'eq',
        Lexer.NE: 'ne',
        Lexer.PLUS: 'add',
        Lexer.MINUS: 'sub',
        Lexer.ASTERISK: 'mul',
        Lexer.SLASH: 'div',
        Lexer.GLOBAL: 'global'
        
        }
    prefix = "  " * indent
    if type(node) != Node or node.kind is None:
        return
    if node.kind == Parser.BINOP or node.kind == Parser.UNARY:
        print(f"{prefix}Node(kind={nodes_table[node.kind]}, value={ops_table[node.value]})")
    else:
        print(f"{prefix}Node(kind={nodes_table[node.kind]}, value={node.value})")
    for child in node.childs:
        print_ast(child, indent + 1)
