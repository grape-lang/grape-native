# The Grape Programming Language

This is a rewrite of the Python interpreter of the Grape Programming Language. It is
designed to be able to compile to native code using [PyPy](https://www.pypy.org).

Having a _compiled_ interpreter should be A LOT quicker than an interpreter in
_interpreted_ python ;)

> Unfortunately my new parsing method, which I REALLY like, doesn't work well in
> Python, so I'm once again rewriting. In Lua this time!

## Design

### Grammar

```text
program       -> statement* EOF ;

statement     -> expression NEWLINE ;
expression    -> function | assignment | if | scoped | logic_or ;

function      -> named | lamda ;
named         -> "fn" IDENTIFIER "(" arguments? ")" block ;
lambda        -> "fn(" arguments? ")" block ;

arguments     -> IDENTIFIER ("," IDENTIFIER)* ;


assignment    -> IDENTIFIER "=" expression ;
if            -> "if" "(" logic_or ")" scoped

scoped        -> block | line
block         -> "do" statement* "end" ;
line          -> expression

logic_or      -> logic_and ( "or" logic_and )* ;
logic_and     -> equality ( "and" equality )* ;
equality      -> comparison ( ( "==" | "!=" ) comparison )* ;
comparison    -> term ( ( ">" | ">=" | "<" | "<=" ) term )* ;
term          -> factor ( ( "+" | "-" ) factor )* ;
factor        -> unary ( ( "/" | "*" | "%" ) unary )* ;
unary         -> ( "-" | "not" ) exponentation ;
exponentation -> call ( "^" expression )
call          -> primary ( "(" collection? ")" )* ;
primary       -> literal | grouping ;


literal       -> number | text | atom | bool | list | tuple | identifier ;

text          -> "\"" ANY "\"";
number        -> "." DIGITS | DIGITS "." DIGITS | DIGITS ;
atom          -> CAPITAL_CHAR + ALPHANUMERIC ;
identifier    -> ALPHANUMERIC ;
bool          -> "true" | "false" ;

list          -> "[" collection "]" ;
tuple         -> "(" collection ")" ;
grouping      -> "(" expression ")" ;

collection    -> expression ("," expression)* ;
```
