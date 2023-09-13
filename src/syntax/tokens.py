from enum import Enum 
from utils import *

class TokenType(Enum):
    LEFT_PAREN = "("
    RIGHT_PAREN = ")"
    LEFT_BRACE = "{"
    RIGHT_BRACE = "}"
    LEFT_BRACKET = "["
    RIGHT_BRACKET = "]"
    COMMA = ","
    DOT = "."
    MINUS = "-"
    PLUS = "+"
    STAR = "*"
    SLASH = "/"
    BACKSLASH = "\\"
    PIPE = "|"
    PIPE_ARROW = "|>"
    ROOF = "^"

    EQUAL = "="
    BANG_EQUAL = "!="
    EQUAL_EQUAL = "=="
    GREATER = ">"
    GREATER_EQUAL = ">="
    LESS = "<"
    LESS_EQUAL = "<="

    IDENTIFIER = 1
    STRING = 2 
    NUMBER = 3
    ATOM = 4

    AND = "and"
    NOT = "not"
    OR = "or"
    NOR = "nor"
    IN = "in"
    FN = "fn"
    PUB = "pub"
    NAMESPACE = "namespace"
    IF = "if"
    ELSEIF = "elseif"
    ELSE= "else"
    USE = "use"
    DO = "do"
    END = "end"
    TRUE = "true"
    FALSE = "false"

    NEWLINE = 5
    EOF = 6

class Token:
    def __init__(self, token_type: TokenType, lexeme: str, literal: any, line: int, col: int):
        self.type = token_type
        self.line = line
        self.col = col

        # The actual string representation of the code, 
        # forexample "if" or "3", or for strings: "\"some text\""
        self.lexeme = lexeme 

        # In case of a literal (basically a value),
        # like, `3` for the lexeme "3" and `"some text"` for the
        # lexeme "\"some text\""
        self.literal = literal
