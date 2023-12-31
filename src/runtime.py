from syntax.tokens import *
from syntax.ast import *
from utils import *

class ANSI:
    OK = '\033[92m'
    WARN = '\033[93m'
    FAIL = '\033[91m'
    NORMAL = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class ErrorHandler:
    def __init__(self, file: str = "unknown"):
        self.hadError = False
        self.file = file

    def error(self, kind: str, line: int, col: int, location: str = "", content: str = "") -> str:   
        header = self.header(self.file, line, col)      
        message = self.message(kind, location, content)

        self.hadError = True
        ErrorReporter.error(message, header)

        return message

    def warn(self, line: int, col: int, content: str = "") -> str:
        header = self.header(self.file, line, col)     
        message = self.message("", "", content)

        ErrorReporter.warn(message, header)

        return message

    def message(self, kind: str, location: str, content: str) -> str:
        message = ""

        if kind and kind != "":
            message += kind
        
        if location and location != "":
            message += " at '" + str(location) + "'"

        if content and content != "":
            if message != "":
                message += ": "
            message += content

        return message

    def header(self, file: str, line: int, col: int) -> str:
        return "[" + file + ":" + str(line) + ":" + str(col) + "]"

class ErrorReporter: 
    def error(message: str, header: str = "Error") -> str:
        print(ANSI.FAIL + ANSI.BOLD + header + ": " + ANSI.NORMAL + message + ".")
        return message

    def warn(message: str, header: str = "Warning") -> str:
        print(ANSI.WARN + ANSI.BOLD + header + ": " + ANSI.NORMAL + message + ".")
        return message

class Debugger:
    def printTokens(tokens: list[Token]) -> None:
        print(Formatter.formatSuccess("Scanned tokens (" + str(len(tokens)) +"):"))
        
        print(Formatter.formatTable(["Lexeme", "Literal", "Token type"]))
        print(Formatter.formatTableSeperator())

        for token in tokens:
            lexeme = str(token.lexeme) if token.lexeme != "\n" else "\\n"
            literal = token.literal or ""

            print(Formatter.formatTable([lexeme, str(literal), str(token.type.name)]))
        
        print("")

    def printAST(expressions: list[Expr]) -> None:
        print(Formatter.formatSuccess("Parsed expressions (" + str(len(expressions)) +"):"))
        for expression in expressions:
            print(expression)

        print("")

    def printRunning() -> None:
        print(Formatter.formatSuccess("Running program"))

    def printError() -> None:
        print(Formatter.formatError("An error occured while running your program. Please check the stacktrace above."))

    def printDone() -> None:
        print("")
        print(Formatter.formatSuccess("[DONE]"))

class Formatter:
    def formatSuccess(message: str) -> str:
        return Formatter.formatHeading(ANSI.OK + "[OK] " + message)

    def formatError(message: str) -> str:
        return Formatter.formatHeading(ANSI.FAIL + "[ERROR] " + message)

    def formatHeading(heading: str) -> str:
        return ANSI.BOLD + heading + ANSI.NORMAL

    def formatTable(cols: list[str]) -> str:
        output = ""

        for col in cols:
            if col != cols[-1]:
                colLength = 3
                wordTabLength = int((len(str(col)) + 1)/8)
                
                output += col
                for i in range(0, colLength - wordTabLength):
                    output += "\t"

                output += "| "
            else:
                output += col

        return output

    def formatTableSeperator() -> str:
        return "----------------------------------------------------------------"