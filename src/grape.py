#!/usr/bin/env python3

import sys
from runtime import ErrorHandler
from runtime import ErrorReporter
from runtime import Debugger
from parser import Linter
from parser import Lexer
from parser import Analyzer
from utils import *

class CLI:
    def __init__(self, argv):
        (binaryName, argv) = popFirst(argv)

        self.grape = Grape()
        self.name = binaryName
        self.argv = argv
        
        if len(argv) >= 2:
            self.error("Too many arguments provided")
            self.usage()
            exit(64)

        elif len(argv) == 1:
            match argv[0]:
                case "--help":
                    self.description()
                    self.usage()

                case filePath:
                    self.grape.runFile(filePath)
                    if self.grape.errorHandler.hadError: exit(65)

        else:
            grape.startREPL()
        
    def description(self) -> None:
        print("A general purpose programming language made for rapid-pase prototyping.")
        print("")

    def usage(self) -> None:
        print("Usage: ")
        print("  " + self.name + " [options] [path]")
        print("")
        print("OPTIONS:")
        print("  --help: print this help")
        print("  --debug: enable printing of debug info")
        print("")

    def error(self, message: str) -> str:
        ErrorReporter.error(message)
        print("")

class Grape:
    def __init__(self):
        self.debug = True
        self.errorHandler = ErrorHandler()

    def runFile(self, filename: str):
        try:
            source_code = open(filename, "r").read()
            self.errorHandler.file = filename
            self.run(source_code)

        except FileNotFoundError:
            self.errorHandler.file = filename
            self.errorHandler.error("", 0, 0, "", "No such file or directory: '" + filename + "'")

    def startRepl(self):
        repl = Repl()

        while True:
            line = repl.input()
            self.run(line)
            self.errorHandler.hadError = False

    def run(self, source: str): 
        Linter(self, source).lint()

        if self.errorHandler.hadError: return

        tokens = Lexer(self, source).lex()

        if self.errorHandler.hadError: return
        elif self.debug: 
            Debugger.printTokens(tokens)

        ast = Analyzer(self, tokens).analyze()

        if self.errorHandler.hadError: return
        elif self.debug: 
            Debugger.printAST(ast)
            Debugger.printRunning()
        
        # Interpreter(self, ast).interpret()

        if self.debug:
            if self.errorHandler.hadError:
                Debugger.printError()
            else:
                Debugger.printDone()

if __name__ == "__main__":
    CLI(sys.argv)
