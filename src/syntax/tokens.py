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
    PERCENT = "%"

    # Binary operators
    AND = "and"
    NOT = "not"
    OR = "or"
    NOR = "nor"
    IN = "in"
    EQUAL = "="
    BANG_EQUAL = "!="
    EQUAL_EQUAL = "=="
    GREATER = ">"
    GREATER_EQUAL = ">="
    LESS = "<"
    LESS_EQUAL = "<="

    # Literals
    IDENTIFIER = 1
    STRING = 2 
    NUMBER = 3
    ATOM = 4
    TRUE = "true"
    FALSE = "false"

    # Blocks
    FN = "fn"
    IF = "if"
    ELSE= "else"
    DO = "do"
    END = "end"
    
    # Namespaces
    NAMESPACE = "namespace"
    USE = "use"
    IMPORT = "import"
    PUB = "pub"
    AT = "@"
    EXEC = "$"

    # Whitespace
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