from decimal import * 
from syntax.tokens import *
from syntax.ast import *
from config import * 

# SyntaxError is already used by Python itself
class ParseError(Exception):
    pass

class LintError(Exception):
    pass

class Parser:
    def __init__(self, source: str):
        self.source = source
        self.line = 1
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
        
        # Match a condition (a function)
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
                return ([], input)

        return parse

    def tag_until(self, parser):
        # Match a string
        if isinstance(parser, str):
            return self.tag(lambda c: c != parser)

        # Match a condition (a function)
        elif callable(parser):
            return self.tag(lambda c: not parser(c))

    # Run this 1 or more times.
    def many1(self, parser):
        def parse(input):
            output = []
            ok = false

            while True:
                if input == "" or input == []:
                    break
                    
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
                if input == "" or input == []:
                    break

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

    # Matches the next n chars
    def advance(self, n: int = 1):
        def parse(input):
            if input[0:n] == "\n":
                self.nextLine()

            self.col += 1
            return (input[n:], input[0:n])

        return parse

    # Sets the line and col attributes to the 
    # next line.
    def nextLine(self):
        self.col = 0
        self.line += 1

class Lexer(Parser):
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

    def lex(self):
        try:
            output = self.parser(self.source)
            
            if output[0] != "":
                nextToken = output[0].split()[0]
                raise ParseError("Unexpected '" + nextToken + "'")

            tokens = [token for token in output[1] if token is not None]
            tokens.append(Token(TokenType.EOF, "", None, self.line, self.col))
            return tokens

        except ParseError as e:
            self.errorHandler.error("Syntax error", self.line, self.col, "", str(e))

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

        # Parse a whole bunch of formats
        return self.token(self.alt([
            self.tag(isDigit),                                 # 0 
            self.sequence([self.tag(isDigit), self.decimals]), # 0.1
            self.decimals                                      # .1
        ]), TokenType.NUMBER, decimal)(input)

    def decimals(self, input):
        return self.sequence([self.tag("."), self.tag(isDigit)])(input)

    def string(self, input):
        return self.token(self.sequence([
            self.tag('"'), 
            self.tag_until('"'), 
            self.tag('"')
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
        out = self.token(self.tag("\n"), TokenType.NEWLINE)(input)
        self.nextLine()

        return out

class Linter(Lexer):
    def __init__(self, grape, source: str):
        super().__init__(grape, source)

        self.parser = self.anywhere([
            self.unterminatedString,
            self.maxDecimals
        ])

    def anywhere(self, parsers):
        parsers.append(self.advance())
        return self.many0(self.alt(parsers))

    def lint(self):
        try:
            self.parser(self.source)

        except LintError as e:
            self.errorHandler.error("Syntax error", self.line, self.col, "", str(e))            

    def unterminatedString(self, input):
        out = self.tag('"')(input)
    
        if '"' not in out[0]:
            raise LintError("Unterminated string")
        else: 
            return self.string(input)

    def maxDecimals(self, input):
        global MAX_DECIMALS
        out = self.decimals(input)

        # The +1 is because out[1] also
        # includes the leading .
        if len(out[1]) > MAX_DECIMALS + 1:
            self.errorHandler.warn(self.line, self.col, "The maximum amount of decimals is set to " + str(MAX_DECIMALS) + ", your value will be rounded")  

        return out

class Analyzer(Parser):
    def __init__(self, grape, tokens: list[Token]) -> list[Expr]:
        self.errorHandler = grape.errorHandler
        super().__init__(tokens)

        self.parser = self.many0(self.expression)

    def analyze(self):
        try:
            output = self.parser(self.source)
            
            if output[0] != []:
                nextToken = output[0][0]
                raise ParseError("Unexpected '" + nextToken.lexeme + "'")

            expressions = [expression for expression in output[1] if expression is not None]
            return expressions

        except ParseError as e:
            self.errorHandler.error("Syntax error", self.line, self.col, "", str(e))

    def expression(self, input):
        return self.alt([
            self.assignment,
            self.conditional,
            self.scoped,
            self.function,
            self.logicOr,
            self.logicAnd,
            self.equality,
            self.comparison,
            self.term,
            self.factor,
            self.unary,
            self.call,
            self.primary
        ])(input)

    def type(self, token_type: TokenType):
        def parse(input):
            out = self.advance()(input)
            
            if out[1][0].type == token_type:
                return out
            else:
                raise ParseError

        return parse

    def assignment(self, input):
        out = self.sequence([
            self.type(TokenType.IDENTIFIER),
            self.type(TokenType.EQUAL),
            self.expression
        ])(input)

        name = out[1][0]
        initializer = out[1][2]
        
        return (out[0], Assignment(name, initializer))

    def conditional(self, input):
        out = self.sequence([
            self.type(TokenType.IF),
            self.type(TokenType.LEFT_PAREN),
            self.expression,
            self.type(TokenType.RIGHT_PAREN),
            self.alt([self.doElseBlock, self.scoped])
        ])(input)

        condition = out[1][2]
        body = out[1][4]

        if isinstance(body, Scoped):
            thenBranch = body
            elseBranch = None

        elif isinstance(body, tuple):
            thenBranch = body[0]
            elseBranch = body[1]

        else:
            raise ParseError("Invalid body for if condition. An if condition should be followed by either a do-end block, or a do-else-end block.")

        return (out[0], Conditional(condition, thenBranch, elseBranch))

    def scoped(self, input):
        return self.alt([
            self.doLine,
            self.doBlock,
        ])(input)

    def doLine(self, input):
        out = self.sequence([
            self.type(TokenType.DO),
            self.expression,
            self.type(TokenType.NEWLINE)
        ])(input)

        expression = out[1][1]
        return (out[0], Line(expression))
        
    def doBlock(self, input):
        out = self.sequence([
            self.type(TokenType.DO),
            self.body,
            self.type(TokenType.END)
        ])(input)

        expressions = out[1][1]
        return (out[0], Block(expressions))

    def doElseBlock(self, input):
        out = self.sequence([
            self.type(TokenType.DO),
            self.body,
            self.type(TokenType.ELSE),
            self.body,
            self.type(TokenType.END)
        ])(input)

        thenBranch = Block(out[1][1])
        elseBranch = Block(out[1][3])

        return (out[0], (thenBranch, elseBranch))

    def body(self, input):
        return self.many1(self.alt([
            self.expression, 
            self.ignore(self.type(TokenType.NEWLINE))
        ]))(input)

    def function(self, input):
        return self.alt([
            self.named,
            self.anonymous,
        ])(input)

    def named(self, input):
        out = self.sequence([
            self.type(TokenType.FN),
            self.type(TokenType.IDENTIFIER),
            self.parameters,
            self.scoped
        ])(input)

        name = out[1][1]
        parameters = out[1][2]
        body = out[1][3]

        return (out[0], Named(name, parameters, body))

    def anonymous(self, input):
        out = self.sequence([
            self.type(TokenType.FN),
            self.parameters,
            self.scoped
        ])(input)

        parameters = out[1][1]
        body = out[1][2]

        return (out[0], Lambda(parameters, body))

    def parameters(self, input):
        return self.sequence([
            self.ignore(self.type(TokenType.LEFT_PAREN)),
            self.comma0(self.type(TokenType.IDENTIFIER)),
            self.ignore(self.type(TokenType.RIGHT_PAREN)),
        ])(input)

    def binary(self, parser):
        def parse(input):
            out = self.sequence([
                self.expression,
                parser,
                self.expression
            ])(input)

            left = out[1][0]
            operator = out[1][1]
            right = out[1][2]

            return (out[0], Binary(left, operator, right))

        return parse

    def logicOr(self, input):
        return self.binary(self.type(TokenType.OR))(input)

    def logicAnd(self, input):
        return self.binary(self.type(TokenType.AND))(input)

    def equality(self, input):
        return self.binary(self.alt([
            self.type(TokenType.EQUAL_EQUAL), 
            self.type(TokenType.BANG_EQUAL)
        ]))(input)

    def comparison(self, input):
        return self.binary(self.alt([
            self.type(TokenType.GREATER), 
            self.type(TokenType.GREATER_EQUAL),
            self.type(TokenType.LESS),
            self.type(TokenType.LESS_EQUAL)
        ]))(input)

    def term(self, input):
        return self.binary(self.alt([
            self.type(TokenType.PLUS), 
            self.type(TokenType.MINUS)
        ]))(input)

    def factor(self, input):
        return self.binary(self.alt([
            self.type(TokenType.SLASH), 
            self.type(TokenType.STAR)
        ]))(input)

    def unary(self, parser, operator):
        def parse(input):
            out = self.sequence([
                operator,
                self.unary(parser, operator)
            ])(input)

            operator = out[1][0]
            right = out[1][1]

            return (out[0], Unary(operator, right))                

        return parse

    def negation(self, input):
        return self.alt([
            self.call, 
            self.unary(self.call, self.alt([
                self.type(TokenType.MINUS),
                self.type(TokenType.NOT)
            ]))
        ])(input)

    def call(self, input):
        out = self.sequence([
            self.expression,
            self.arguments
        ])(input)

        callee = out[1][0]
        arguments = out[1][1]

        return (out[0], Call(callee, arguments))

    def arguments(self, input):
        return self.sequence([
            self.ignore(self.type(TokenType.LEFT_PAREN)),
            self.collection,
            self.ignore(self.type(TokenType.RIGHT_PAREN)),
        ])(input)

    def primary(self, input):
        return self.alt([
            self.literal,
            self.variable,
            self.boolean,
            self.list,
            self.tuple,
            self.grouping
        ])(input)

    def literal(self, input):
        out = self.alt([
            self.type(TokenType.NUMBER),
            self.type(TokenType.STRING),
            self.type(TokenType.ATOM),
        ])(input)

        return (out[0], Literal(out[1]))

    def variable(self, input):
        out = self.type(TokenType.IDENTIFIER)(input)
        return (out[0], Variable(out[1]))

    def boolean(self, input):
        out = self.alt([
            self.type(TokenType.TRUE),
            self.type(TokenType.FALSE)
        ])(input)

        return (out[0], Literal(out[1]))

    def list(self, input):
        out = self.sequence([
            self.ignore(self.type(TokenType.LEFT_BRACKET)),
            self.collection,
            self.ignore(self.type(TokenType.RIGHT_BRACKET))
        ])(input)

        items = out[1][1]
        return (out[0], List(items))

    def tuple(self, input):
        out = self.sequence([
            self.type(TokenType.LEFT_BRACE),
            # A tuple can't have just one value, otherwise it is considered a grouping
            self.comma1(self.expression),
            self.type(TokenType.RIGHT_BRACKE)
        ])(input)

        items = out[1][1]
        return (out[0], Tuple(items))

    def collection(self, input):
        return self.comma0(self.expression)(input)

    def grouping(self, input):
        out = self.expression(input)
        return (out[0], Grouping(out[1]))

    # Comma separated lists with at least 0 item
    def comma0(self, parser):
        def parse(input):
            try:
                return self.comma1(parser)
            except ParseError:
                return (input, [])
    
    # Comma separated lists with at least 1 item
    def comma1(self, parser):
        return self.sequence([
            parser,
            self.many0(self.sequence([
                self.ignore(self.type(TokenType.COMMA)),
                parser
            ]))
        ])
