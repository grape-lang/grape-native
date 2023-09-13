# The Grape Programming Language

This is a rewrite of the Python interpreter of the Grape Programming Language. It is
designed to be able to compile to native code using [PyPy](https://www.pypy.org).

Having a _compiled_ interpreter should be A LOT quicker than an interpreter in
_interpreted_ python ;)

## Design

### Grammar

```text
program     -> statement* EOF ;

statement   -> expression NEWLINE ;
expression  -> variable | if | function | do | logic_or ;

function    -> named | lamda ;
assignment  -> IDENTIFIER "=" expression ;
if          -> "if" "(" logic_or ")" scoped
named       -> "fn" IDENTIFIER "(" arguments? ")" block ;
lambda      -> "fn(" arguments? ")" block ;

scoped      -> block | line
block       -> "do" statement* "end" ;
line        -> expression

logic_or    -> logic_and ( "or" logic_and )* ;
logic_and   -> equality ( "and" equality )* ;
equality    -> comparison ( ( "==" | "!=" ) comparison )* ;
comparison  -> term ( ( ">" | ">=" | "<" | "<=" ) term )* ;
term        -> factor ( ( "+" | "-" ) factor )* ;
factor      -> unary ( ( "/" | "*" ) unary )* ;
unary       -> ( "-" | "not" ) unary | call ;
call        -> primary ( "(" arguments? ")" )* ;
primary     -> literal | grouping ;

arguments   -> IDENTIFIER ("," IDENTIFIER)* ;

literal     -> NUMBER | TEXT | ATOM | bool | list | tuple | IDENTIFIER ;
bool        -> "true" | "false" ;
list        -> "[" collection "]" ;
tuple       -> "(" collection ")" ;
grouping    -> "(" expression ")" ;

collection  -> expression ("," expression)* ;
```
