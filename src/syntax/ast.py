from syntax.tokens import *

# In Grape everything is an expression

class Expr():
    pass

# High level expressions
# These are usually statements in other languages.

class Assignment(Expr):
    def __init__(self, name: Token, initializer: Expr):
        self.name = name
        self.expression = initializer

class Scoped(Expr):
    pass

class Block(Scoped):
    def __init__(self, expressions: list[Expr]):
        self.expressions = expressions

class Line(Scoped):
    def __init__(self, expression: Expr):
        self.expression = expression

class If(Expr):
    def __init__(self, condition: Expr, ifBranch: Scoped, elseBranch: Scoped = None):
        self.condition = condition
        self.ifBranch = ifBranch
        self.elseBranch = elseBranch

class Function(Expr):
    def __init__(self, parameters: list[Token], body: Scoped):
        self.parameters = parameters
        self.body = body

class Named(Function):
    def __init__(self, name: Token, parameters: list[Token], body: Scoped):
        self.name = name
        super().__init__(parameters, body)

class Lambda(Function):
    pass

# Logical operators

class Operator(Expr):
    def __init__(self, operator: Token, right: Expr):
        self.operator = operator
        self.right = right

class Unary(Operator):
    pass

class Binary(Operator):
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        super().__init__(operator, right)

# Literals

class Call(Expr):
    def __init__(self, callee: Expr, arguments: list[Expr], closingParenToken: Token):
        self.callee = callee
        self.arguments = arguments

        # This is needed to show the location of the error
        # when raising type errors later
        self.closingParenToken = closingParenToken

class Variable(Expr):
    def __init__(self, name: Token):
        self.name = name

class Grouping(Expr):
    def __init__(self, expression: Expr):
        self.expression = expression

class Literal(Expr):
    def __init__(self, value):
        self.value = value

class Collection(Expr):
    def __init__(self, items: list[Expr]):
        self.items = items
    
class List(Collection):
    pass

class Tuple(Collection):
    pass
