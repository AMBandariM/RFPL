import sys
import traceback
from antlr4 import *
from dataclasses import dataclass
from typing import Callable
from antlr4.error.ErrorListener import ErrorListener
from antlr4.error.Errors import ParseCancellationException
from typing import Union, List

from .RFPLLexer import RFPLLexer
from .RFPLParser import RFPLParser
from .natural import Natural

DEBUG = False
def debug(*args):
    if not DEBUG:
        return
    print(*args, file=sys.stderr)


@dataclass
class SymbolEntry:
    symbol: str
    call: Callable
    builtin: bool = False


class SymbolTable:
    def __init__(self):
        self.table: List[SymbolEntry] = []
    
    def search(self, symbol: str, index: int = -1): 
        index = len(self.table) - 1
        while index >= 0 and self.table[index].symbol != symbol:
            index -= 1
        if index < 0:
            return None
        return self.table[index]
    
    def addEntry(self, entry: SymbolEntry):
        self.table.append(entry)
    
    def add(self, *args, **kwargs):
        return self.addEntry(SymbolEntry(*args, **kwargs))


@dataclass
class BaseList:
    args: List[RFPLParser.FexprContext]
    prev: 'BaseList' = None


class Interpreter:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.symbol_table.add(
            symbol='S', 
            call=lambda _blist, args : args[0].succ(), 
            builtin=True
        )

    def load_basics(self):
        self.symbol_table.add(
            symbol='Add',
            call=lambda _blist, args : args[0].add(args[1]),
            builtin=True
        )
        self.symbol_table.add(
            symbol='Mul',
            call=lambda _blist, args : args[0].multiply(args[1]),
            builtin=True
        )
        self.symbol_table.add(
            symbol='Pow',
            call=lambda _blist, args : args[1].power(args[0]),
            builtin=True
        )
        self.symbol_table.add(
            symbol='Get',
            call=lambda _blist, args : args[1].getEntry(args[0]),
            builtin=True
        )
        self.symbol_table.add(
            symbol='Set',
            call=lambda _blist, args : args[2].setEntry(args[0], args[1]),
            builtin=True
        )
        self.symbol_table.add(
            symbol='Int',
            call=lambda _blist, args : args[0].simplify() or args[0],
            builtin=True
        )
        self.symbol_table.add(
            symbol='List',
            call=lambda _blist, args : args[0].factor() or args[0],
            builtin=True
        )
        return Natural(0)

    def interpretFexpr(self, tree, blist: BaseList, args: List[Natural]) -> Natural:
        if not isinstance(tree, RFPLParser.FexprContext):
            raise Exception('tree must represent a fexpr, got {}'.format(type(tree)))
        tree = tree.getChild(0)
        if isinstance(tree, RFPLParser.FexprleafContext):
            base_nxt = []
            if tree.fexprlist() is not None:
                fexprlist: RFPLParser.FexprlistContext = tree.fexprlist()
                base_nxt += fexprlist.getTypedRuleContexts(RFPLParser.FexprContext)
            symb = tree.Symbol().getText()
            syment = tree.children[-1]
            if syment is None:
                raise Exception('function {} not defined'.format(symb))
            return syment.call(BaseList(base_nxt, blist), args)
        elif isinstance(tree, RFPLParser.BracketContext):
            if blist is None:
                raise Exception('root function have no base argument')
            ind = Natural.interpret(tree.natural()).toInt()
            if ind >= len(blist.args):
                raise Exception('not enough base arguments')
            return self.interpretFexpr(blist.args[ind], blist.prev, args)
        elif isinstance(tree, RFPLParser.IdentityContext):
            ind = Natural.interpret(tree.natural()).toInt()
            debug(ind, args)
            if ind >= len(args):
                raise Exception('not enough arguments')
            return args[ind]
        elif isinstance(tree, RFPLParser.ConstantContext):
            return Natural.interpret(tree.natural())
        elif isinstance(tree, RFPLParser.BuiltinCnContext):
            f, *gs = tree.fexprlist().getTypedRuleContexts(RFPLParser.FexprContext)
            fargs = []
            for g in gs:
                gres = self.interpretFexpr(g, blist, args)
                fargs.append(gres)
            return self.interpretFexpr(f, blist, fargs)
        elif isinstance(tree, RFPLParser.BuiltinPrContext):
            if len(args) == 0:
                raise Exception('not enough arguments for Pr')
            f = tree.fexpr(0)
            g = tree.fexpr(1)
            n = args[0].toInt()
            cur = self.interpretFexpr(f, blist, args[1:])
            args = [None, None] + args[1:]
            for i in range(n):
                args[0] = cur
                args[1] = Natural(i)
                cur = self.interpretFexpr(g, blist, args)
            return cur
        elif isinstance(tree, RFPLParser.BuiltinMnContext):
            f = tree.fexpr(0)
            args = [Natural(0)] + args
            while not self.interpretFexpr(f, blist, args).isZero():
                args[0].natural += 1
            return args[0]
        else:
            raise Exception('unknown node {}'.format(type(tree)))

    def interpretNexpr(self, tree):
        if not isinstance(tree, RFPLParser.NexprContext):
            raise Exception('tree must represent a nexpr, got {}'.format(type(tree)))
        if tree.natural() is not None:
            return Natural.interpret(tree.natural())
        fexpr: RFPLParser.FexprContext = tree.fexpr()
        nexprlist: RFPLParser.NexprlistContext = tree.nexprlist()
        args = []
        for nexpr in nexprlist.getTypedRuleContexts(RFPLParser.NexprContext):
            args.append(self.interpretNexpr(nexpr))
        self.preproc(fexpr)
        return self.interpretFexpr(fexpr, None, args)

    class ThrowingErrorListener(ErrorListener):
        def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
            ex = ParseCancellationException(f'line {line}: {column} {msg}')
            ex.line = line
            ex.column = column
            raise ex

    def preproc(self, tree):
        tree = tree.getChild(0)
        if isinstance(tree, RFPLParser.FexprleafContext):
            base_nxt = []
            if tree.fexprlist() is not None:
                fexprlist: RFPLParser.FexprlistContext = tree.fexprlist()
                base_nxt += fexprlist.getTypedRuleContexts(RFPLParser.FexprContext)
            symb = tree.Symbol().getText()
            syment = self.symbol_table.search(symb)
            if syment is None:
                raise Exception(f'function {symb} not defined')
            tree.children.append(syment)
            for func in base_nxt:
                self.preproc(func)
        elif isinstance(tree, RFPLParser.BracketContext):
            pass
        elif isinstance(tree, RFPLParser.IdentityContext):
            pass
        elif isinstance(tree, RFPLParser.ConstantContext):
            pass
        elif isinstance(tree, RFPLParser.BuiltinCnContext):
            f, *gs = tree.fexprlist().getTypedRuleContexts(RFPLParser.FexprContext)
            for g in gs:
                self.preproc(g)
            self.preproc(f)
        elif isinstance(tree, RFPLParser.BuiltinPrContext):
            f = tree.fexpr(0)
            g = tree.fexpr(1)
            self.preproc(f)
            self.preproc(g)
        elif isinstance(tree, RFPLParser.BuiltinMnContext):
            self.preproc(f)
        else:
            raise Exception(f'unknown node {type(tree)}')


    def interpret(self, line:str):
        try:
            input_stream = InputStream(line.strip())
            lexer = RFPLLexer(input_stream)
            lexer.removeErrorListeners()
            lexer.addErrorListener(self.ThrowingErrorListener())

            token_stream = CommonTokenStream(lexer)

            parser = RFPLParser(token_stream)
            parser.removeErrorListeners()
            parser.addErrorListener(self.ThrowingErrorListener())

            tree = parser.line()

            tree = tree.getChild(0)
            if isinstance(tree, RFPLParser.DefineContext):
                symb = tree.Symbol().getText()
                fexpr = tree.fexpr()
                self.preproc(fexpr)
                message = f'Function {symb} added'
                syment = self.symbol_table.search(symb)
                if syment is not None:
                    if syment.builtin:
                        raise Exception('cannot redefine builtin function {}'.format(symb))
                    message = f'Function {symb} redefined'
                self.symbol_table.add(
                    symbol=symb,
                    call=lambda blist, args, fexpr=fexpr: self.interpretFexpr(fexpr, blist, args)
                )
                return 'Success', message
            elif isinstance(tree, RFPLParser.ExamineContext):
                result = self.interpretNexpr(tree.nexpr())
                return 'Success', result
            else:
                raise Exception('unknown node {}'.format(type(tree)))  # I leave this one !
        except Exception as e:
            return f'ERROR: {e}', None
