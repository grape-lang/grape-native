from decimal import * 
from syntax.tokens import *
from config import * 

# ParseErroror is already used by Python itself
class ParseError(BaseException):
    pass

class Parser:
    def __init__(self, source: str):
        self.source = source
        self.line = 0
        self.col = 0
    
    def ignore(self, parser):
        def parse(input):
            output = parser(input)
            return (output[0], None) 
        return parse

    # Match a string or match every character for
    # which the given condition (a function) returns true.
    def tag(self, parser):

        # Match a string
        if isinstance(parser, str):
            def parse(input):
                # Don't match inputs that are shorter
                # than the parser.
                if len(input) < len(parser):
                    raise ParseError

                if input[0:len(parser)] == parser:
                    self.col += len(parser)
                    return (input[len(parser):], parser)

                raise ParseError
        
        # Match a condition (a fucntion)
        elif callable(parser):
            def parse(input):
                col = self.col
                for i in range(len(input)):
                    col += 1

                    # Loop until a character doesn't match
                    # the given condition (a function)
                    if not parser(input[i]):
                        if i == 0:
                            raise ParseError

                        self.col = col
                        return (input[i:], input[0:i])

                # Don't match empty strings
                if len(input) == 0:
                    raise ParseError

                # If the full string matches
                # (because it didn't return in the for loop)
                return ("", input)
        return parse

    # Run this 1 or more times.
    def many1(self, parser):
        def parse(input):
            output = []
            ok = false

            while True:
                try:
                    p = parser(input)
                    input = p[0]
                    output.append(p[1])
                    ok = true

                except ParseError:
                    break

            if ok: 
                return (input, output)
            else: 
                raise ParseError
        return parse

    # Run this 0 or more times.
    def many0(self, parser):
        def parse(input):
            output = []

            while True:
                try:
                    p = parser(input)
                    input = p[0]
                    output.append(p[1])

                except ParseError:
                    break

            return (input, output)
        return parse

    # Try every parser given
    # and return the output of the first one that works.
    def alt(self, parsers):
        def parse(input):
            for parser in parsers:
                try:
                    return parser(input)

                except ParseError:
                    pass
                
            raise ParseError
        return parse

    # Match if the given parsers match in the
    # correct order
    def sequence(self, parsers):
        def parse(input):
            output = ""

            for parser in parsers:
                out = parser(input)
                input = out[0]
                output += out[1]
            
            return (input, output)
        return parse
                    
class Tokenizer(Parser):
    def __init__(self, grape, source: str):
        self.errorHandler = grape.errorHandler
        super().__init__(source)

        self.parser = self.many0(self.alt([
            self.operator,
            self.brackets,
            self.keyword,
            self.number,
            self.string,    
            self.boolean,
            self.identifier,
            self.punctuation,
            self.whitespace,
            self.newline
        ]))

    def tokenize(self):
        try:
            output = self.parser(self.source)
            tokens = [token for token in output[1] if token is not None]

            tokens.append(Token(TokenType.EOF, "", None, self.line, self.col))
            return tokens

        except ParseError as e:
            message = e.message
            self.errorHandler.report("Syntax error", self.line, self.col, "", message)

    # Map the output of a parser to a token.
    # Accepts an optional argument for converting the 
    # lexeme to a literal.
    def token(self, parser, token_type, literal = (lambda x: None)):
        def parse(input):
            output = parser(input)
            lexeme = output[1]

            token = Token(token_type, lexeme, literal(lexeme), self.line, self.col)

            return (output[0], token)

        return parse

    def operator(self, input):
        return self.alt([
            self.token(self.tag("+"), TokenType.PLUS),
            self.token(self.tag("-"), TokenType.MINUS),
            self.token(self.tag("*"), TokenType.STAR),
            self.token(self.tag("/"), TokenType.SLASH),
            self.token(self.tag("^"), TokenType.ROOF),
            self.token(self.tag("%"), TokenType.PERCENT),
            self.token(self.tag("=="), TokenType.EQUAL_EQUAL),
            self.token(self.tag("="), TokenType.EQUAL),
            self.token(self.tag("!="), TokenType.BANG_EQUAL),
            self.token(self.tag(">="), TokenType.GREATER_EQUAL),
            self.token(self.tag(">"), TokenType.GREATER),
            self.token(self.tag("<="), TokenType.LESS_EQUAL),
            self.token(self.tag("<"), TokenType.LESS_EQUAL),
            self.token(self.tag("in"), TokenType.IN),
            self.token(self.tag("and"), TokenType.AND),
            self.token(self.tag("not"), TokenType.NOT),
            self.token(self.tag("or"), TokenType.OR),
            self.token(self.tag("nor"), TokenType.NOR),
        ])(input)

    def punctuation(self, input):
        return self.alt([
            self.token(self.tag("\\"), TokenType.BACKSLASH),
            self.token(self.tag("|>"), TokenType.PIPE_ARROW),
            self.token(self.tag("|"), TokenType.PIPE),
            self.token(self.tag("."), TokenType.DOT),
            self.token(self.tag(":"), TokenType.DOT),
            self.token(self.tag(","), TokenType.COMMA)
        ])(input)

    def brackets(self, input):
        return self.alt([
            self.token(self.tag("("), TokenType.LEFT_PAREN),
            self.token(self.tag(")"), TokenType.RIGHT_PAREN),
            self.token(self.tag("{"), TokenType.LEFT_BRACE),
            self.token(self.tag("}"), TokenType.RIGHT_BRACE),
            self.token(self.tag("["), TokenType.LEFT_BRACKET),
            self.token(self.tag("]"), TokenType.RIGHT_BRACKET)
        ])(input)

    def keyword(self, input):
        return self.alt([
            self.token(self.tag("fn"), TokenType.FN),
            self.token(self.tag("if"), TokenType.IF),
            self.token(self.tag("else"), TokenType.ELSE),
            self.token(self.tag("do"), TokenType.DO),
            self.token(self.tag("end"), TokenType.END),

            # Namespaces
            self.token(self.tag("namespace"), TokenType.NAMESPACE),
            self.token(self.tag("use"), TokenType.USE),
            self.token(self.tag("import"), TokenType.IMPORT),
            self.token(self.tag("pub"), TokenType.PUB),
            self.token(self.tag("@"), TokenType.AT),
            self.token(self.tag("$"), TokenType.EXEC)
        ])(input)    

    def number(self, input):
        global MAX_DECIMALS
        decimal = lambda d: round(Decimal(d), MAX_DECIMALS)
        decimals = self.sequence([self.tag("."), self.tag(isDigit)])

        # Parse a whole bunch of formats
        return self.token(self.alt([
            self.tag(isDigit),                            # 0 
            self.sequence([self.tag(isDigit), decimals]), # 0.1
            decimals                                      # .1
        ]), TokenType.NUMBER, decimal)(input)

    def string(self, input):
        return self.token(self.sequence([
            self.tag("\""), 
            self.tag(lambda c: c != "\""), 
            self.tag("\"")
        ]), TokenType.STRING, str)(input)

    def boolean(self, input):
        return self.alt([
            self.token(self.tag("true"), TokenType.TRUE, bool),
            self.token(self.tag("false"), TokenType.FALSE, bool)
        ])(input)

    def identifier(self, input):
        return self.token(self.tag(lambda c: isAlphaNumeric(c) or c in ["_"]), TokenType.IDENTIFIER)(input)

    def whitespace(self, input):
        return self.alt([
            self.ignore(self.tag(" ")),
            self.ignore(self.tag("\r")),
            self.ignore(self.tag("\t"))
        ])(input)

    def newline(self, input):
        return self.token(self.tag("\n"), TokenType.NEWLINE)(input)

def isAlpha(char):
    return char.isalpha()
    
def isDigit(char):
    return char.isdigit()

def isAlphaNumeric(char):
    return isAlpha(char) or isDigit(char)

def isCapital(char):
    return isAlpha(char) and char in charRange("A", "Z")