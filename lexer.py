import sys, string
from io import StringIO
from preprocessor import Preprocessor

class Lexer:

    NUM, IDENT, \
    LSQR, RSQR, LBRA, RBRA, LPAR, RPAR, \
    PLUS, MINUS, ASTERISK, SLASH, PERCENT, \
    DOUBLE_EQ, NE, LT, LE, GT, GE, \
    DOUBLE_AMPER, DOUBLE_PIPE, \
    EQ, EX_MARK, SEMICOLON, COLON, COMMA, \
    USE, FN, GLOBAL, IF, ELSE, WHILE, RET, \
    EOF, \
    = range(34)

    SYMBOLS = {
        '[': LSQR, ']': RSQR,
        '{': LBRA, '}': RBRA,
        '(': LPAR, ')': RPAR,
        '+': PLUS, '-': MINUS,
        '*': ASTERISK, '/': SLASH, '%': PERCENT,
        ';': SEMICOLON, ':': COLON, ',': COMMA
        }

    DOUBLE_SYMBOLS = {
        '=': {'=': DOUBLE_EQ, None: EQ},
        '<': {'=': LE, None: LT},
        '>': {'=': GE, None: GT},
        '!': {'=': NE, None: EX_MARK},
        '&': {'&': DOUBLE_AMPER},
        '|': {'|': DOUBLE_PIPE},
        }

    KEYWORDS = {
        'use': USE,
        'fn': FN,
        'global': GLOBAL,
        'if': IF,
        'else': ELSE,
        'while': WHILE,
        'ret': RET,
        }

    ch = ' '

    def __init__(self, text):
        if text is None:
            self.stream = open(sys.argv[1])
        else:
            self.stream = StringIO(text)

        preprocessor = Preprocessor(self.stream)
        self.stream = preprocessor.read()

        self.line = 1
        self.cursor = 1

    def getch(self):
        self.ch = self.stream.read(1)
        
        if self.ch in ('\n', '\r'):
            self.line += 1
            self.cursor = 1
        else:
            self.cursor += 1

    def get_token(self):
        token_type = None
        token_value = None
        
        while token_type is None:
            if not len(self.ch):
                token_type = Lexer.EOF               
                return token_type, token_value, self.line, self.cursor
            elif self.ch.isspace():
                self.getch()
                
            elif self.ch.isdigit():
                token_type = Lexer.NUM
                token_value = ''
                
                while self.ch.isdigit():
                    token_value += self.ch
                    self.getch()
                token_value = int(token_value)

                return token_type, token_value, self.line, self.cursor
            elif self.ch in string.ascii_letters or self.ch == '_':
                value = ''
                
                while self.ch in string.ascii_letters or self.ch.isdigit() or self.ch == '_':
                    value += self.ch
                    self.getch()
                    
                if value in Lexer.KEYWORDS:
                    token_type = Lexer.KEYWORDS[value]
                else:
                    token_type = Lexer.IDENT
                    token_value = value

                return token_type, token_value, self.line, self.cursor
            elif self.ch in Lexer.SYMBOLS:
                token_type = Lexer.SYMBOLS[self.ch]
                self.getch()
                return token_type, token_value, self.line, self.cursor
            elif self.ch in Lexer.DOUBLE_SYMBOLS:
                first_ch = self.ch
                self.getch()
                
                second_ch = self.ch
                if second_ch in Lexer.DOUBLE_SYMBOLS[first_ch]:
                    token_type = Lexer.DOUBLE_SYMBOLS[first_ch][double_ch]
                else:
                    token_type = Lexer.DOUBLE_SYMBOLS[first_ch][None]

                return token_type, token_value, self.line, self.cursor

#p = Lexer(
'''fn add[a, b]
{
    ret a + b;
}

fn main[]
{
    x = 15;
    global y = 10;
    z = add[x, y];
    ret 0;
}'''
#)

#print(p.get_token())
