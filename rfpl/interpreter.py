import sys
import traceback
from antlr4 import *
from dataclasses import dataclass
from typing import Callable
from antlr4.error.ErrorListener import ErrorListener
from antlr4.error.Errors import ParseCancellationException
from typing import Union, List
import hashlib
import random

from .RFPLLexer import RFPLLexer
from .RFPLParser import RFPLParser
from .natural import Natural, NaturalList

DEBUG = True
def debug(*args):
    if not DEBUG:
        return
    print(*args, file=sys.stderr)


@dataclass
class BaseList:
    args: List[RFPLParser.FexprContext]
    prev: 'BaseList' = None


@dataclass
class SymbolEntry:
    symbol: str
    call: Callable[[BaseList, NaturalList], Natural]
    builtin: bool = False
    ix: int = -1
    basesz: int = 0


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
        entry.ix = len(self.table)
        self.table.append(entry)
    
    def add(self, *args, **kwargs):
        return self.addEntry(SymbolEntry(*args, **kwargs))


class HashCache:
    CACHE = True

    def __init__(self, basic_functions):
        self.basic_functions = basic_functions
        self.cache = {}
        self.possibleMatches = {}
        self.counter = {}
        self.counter_max = 20

    def hash(self, args: NaturalList):
        lst = ''
        started = False
        for arg in args.content[::-1]:
            iii = arg.toInt()
            if iii:
                started = True
            iii %= 600851475143
            if started:
                lst += str(iii) + '-'
        return hashlib.md5(lst.encode()).hexdigest()

    def makeMockNaturalList(self, n: int):
        m = int(n**0.5)
        a, b, c = random.randint(0,m), random.randint(0,m), random.randint(0,m)
        return NaturalList([Natural(a), Natural(b), Natural(c), Natural(None), Natural(None)])

    def callAndCache(self, fun: SymbolEntry, blist: BaseList, args: List[Natural]):
        if (blist is not None and len(blist.args)) or fun.builtin or not self.CACHE:
            return fun.call(blist, args)
        if fun.ix not in self.possibleMatches:
            self.possibleMatches[fun.ix] = self.basic_functions.copy()
            self.counter[fun.ix] = 0
            self.cache[fun.ix] = {}
        if self.counter[fun.ix] == self.counter_max:
            return self.possibleMatches[fun.ix][0].call(blist, args)
        hsh = self.hash(args)
        if hsh in self.cache[fun.ix].keys():
            return self.cache[fun.ix][hsh]
        res = fun.call(blist, args)
        intres = res.toInt()
        for ent in self.possibleMatches[fun.ix]:
            rel = ent.call(blist, args)
            if rel.toInt() != intres:
                self.possibleMatches[fun.ix].remove(ent)
        mocknatlst = self.makeMockNaturalList(self.counter[fun.ix])
        for ent in self.possibleMatches[fun.ix]:
            rel = ent.call(None, mocknatlst)
            rez = fun.call(None, mocknatlst)
            if rel.toInt() != rez.toInt():
                self.possibleMatches[fun.ix].remove(ent)
        if len(self.possibleMatches[fun.ix]):
            self.counter[fun.ix] += 1
            if self.counter[fun.ix] == self.counter_max:
                debug(f'replacing {fun.symbol} with {self.possibleMatches[fun.ix][0].symbol} ...')
        self.cache[fun.ix][hsh] = res
        return res


@dataclass
class InputError:
    message: str
    start: int = None
    stop: int = None

    def setContext(self, ctx: ParserRuleContext):
        self.start = ctx.start.start
        self.stop = ctx.stop.stop
        return self

    def toString(self, stream: InputStream = None):
        s = self.message + '\n'
        if self.start is None or self.stop is None or stream is None:
            return s
        s += '  ' + str(stream) + '\n'
        s += '  ' + ' ' * self.start + '^' + '~' * max(0, self.stop - self.start) + '\n'
        return s


class ThrowingErrorListener(ErrorListener):
    def __init__(self, interpreter: 'Interpreter'):
        self.interpreter = interpreter

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.interpreter.errors.append(InputError(f'ERROR: {msg}', offendingSymbol.start, offendingSymbol.stop))


class Interpreter:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.symbol_table.add(
            symbol='S', 
            call=lambda _blist, args : args[0].succ(), 
            builtin=True
        )
        self.basic_arithmetic_enteries = [
            SymbolEntry(
                symbol='Add',
                call=lambda _blist, args : args[0] + args[1],
                builtin=True
            ),
            SymbolEntry(
                symbol='Sub',
                call=lambda _blist, args : args[1] - args[0],
                builtin=True
            ),
            SymbolEntry(
                symbol='Mul',
                call=lambda _blist, args : args[0] * args[1],
                builtin=True
            ),
            SymbolEntry(
                symbol='Pow',
                call=lambda _blist, args : args[1] ** args[0],
                builtin=True
            )
        ]
        
        def _getEntry(_blist, args):
            if args[1].isZero():
                return Natural(0)
            return args[1].getEntry(args[0])
        
        def _setEntry(_blist, args):
            if args[2].isZero():
                return Natural(0)
            return args[2].setEntry(args[0], args[1])
        
        def _int(_blist, args):
            args[0].simplify()
            return args[0]
        
        def _list(_blist, args):
            if args[0].isDefined() and not args[0].isZero():
                args[0].factor()
            return args[0]
        
        self.basic_sequential_enteries = [
            SymbolEntry(
                symbol='Get',
                call=_getEntry,
                builtin=True
            ),
            SymbolEntry(
                symbol='Set',
                call=_setEntry,
                builtin=True
            ),
            SymbolEntry(
                symbol='Int',
                call=_int,
                builtin=True
            ),
            SymbolEntry(
                symbol='List',
                call=_list,
                builtin=True
            ),
        ]
        self.basic_numbertheory_enteries = [
            SymbolEntry(
                symbol='Mod',
                call=lambda _blist, args : args[0] % args[1],
                builtin=True
            ),
        ]
        self.cache = HashCache(
            self.basic_arithmetic_enteries + self.basic_sequential_enteries + self.basic_numbertheory_enteries
        )
        self.errors: List[InputError] = []

    def load_basics(self):
        self.load_basic_arithmetic_enteries()
        self.load_basic_sequential_enteries()
        self.load_basic_numbertheory_enteries()
    
    def load_basic_arithmetic_enteries(self):
        for ent in self.basic_arithmetic_enteries:
            self.symbol_table.addEntry(ent)
    
    def load_basic_sequential_enteries(self):
        for ent in self.basic_sequential_enteries:
            self.symbol_table.addEntry(ent)
    
    def load_basic_numbertheory_enteries(self):
        for ent in self.basic_numbertheory_enteries:
            self.symbol_table.addEntry(ent)

    def interpretFexpr(self, tree, blist: BaseList, args: NaturalList) -> Natural:
        tree = tree.getChild(0)
        if isinstance(tree, RFPLParser.FexprleafContext):
            base_nxt = []
            if tree.fexprlist() is not None:
                fexprlist: RFPLParser.FexprlistContext = tree.fexprlist()
                base_nxt += fexprlist.getTypedRuleContexts(RFPLParser.FexprContext)
            syment = tree.c_syment
            return self.cache.callAndCache(syment, BaseList(base_nxt, blist), args)
        elif isinstance(tree, RFPLParser.BracketContext):
            return self.interpretFexpr(blist.args[tree.c_number], blist.prev, args)
        elif isinstance(tree, RFPLParser.IdentityContext):
            return args[tree.c_number]
        elif isinstance(tree, RFPLParser.ConstantContext):
            return tree.c_natural
        elif isinstance(tree, RFPLParser.BuiltinCnContext):
            f, *gs = tree.fexprlist().getTypedRuleContexts(RFPLParser.FexprContext)
            fargs = []
            for g in gs:
                gres = self.interpretFexpr(g, blist, args)
                fargs.append(gres)
            fargs = NaturalList(fargs)
            return self.interpretFexpr(f, blist, fargs)
        elif isinstance(tree, RFPLParser.BuiltinPrContext):
            f = tree.fexpr(0)
            g = tree.fexpr(1)
            n = args[0].toInt()
            args = args.drop(1)
            cur = self.interpretFexpr(f, blist, args)
            args = NaturalList([Natural(None), Natural(None)]) + args
            for i in range(n):
                args[0] = cur
                args[1] = Natural(i)
                cur = self.interpretFexpr(g, blist, args)
            return cur
        elif isinstance(tree, RFPLParser.BuiltinMnContext):
            f = tree.fexpr()
            args = NaturalList([Natural(0)]) + args
            while not self.interpretFexpr(f, blist, args).isZero():
                args[0] = args[0].succ()
            return args[0]

    def interpretNexpr(self, tree):
        if not isinstance(tree, RFPLParser.NexprContext):
            raise Exception('Tree must represent a nexpr, got {}'.format(type(tree)))
        if tree.natural() is not None:
            return Natural.interpret(tree.natural())
        fexpr: RFPLParser.FexprContext = tree.fexpr()
        nexprlist: RFPLParser.NexprlistContext = tree.nexprlist()
        args = []
        for nexpr in nexprlist.getTypedRuleContexts(RFPLParser.NexprContext):
            args.append(self.interpretNexpr(nexpr))
        self.preprocess(fexpr)
        if self.errors:
            return None
        args = NaturalList(args)
        return self.interpretFexpr(fexpr, None, args)

    def preprocess(self, tree):
        basesz = 0
        tree = tree.getChild(0)
        if isinstance(tree, RFPLParser.FexprleafContext):
            base_nxt = []
            if tree.fexprlist() is not None:
                fexprlist: RFPLParser.FexprlistContext = tree.fexprlist()
                base_nxt += fexprlist.getTypedRuleContexts(RFPLParser.FexprContext)
            symb = tree.Symbol().getText()
            syment = self.symbol_table.search(symb)
            if syment is None:
                self.errors.append(InputError(
                    message=f'ERROR: Function {symb} is not defined',
                ).setContext(tree))
                return basesz
            if len(base_nxt) != syment.basesz:
                self.errors.append(InputError(
                    message=f'ERROR: {symb} accepts {syment.basesz} bases but got {len(base_nxt)}'
                ).setContext(tree))
                return basesz
            tree.children.append(syment)
            tree.c_syment = syment  # custom attribute added to the tree
            for b in base_nxt:
                basesz = max(basesz, self.preprocess(b))
        elif isinstance(tree, RFPLParser.BracketContext):
            tree.c_number = Natural.interpret(tree.natural()).toInt() 
            basesz = max(basesz, tree.c_number + 1)
        elif isinstance(tree, RFPLParser.IdentityContext):
            tree.c_number = Natural.interpret(tree.natural()).toInt()
        elif isinstance(tree, RFPLParser.ConstantContext):
            tree.c_natural = Natural.interpret(tree.natural())
        elif isinstance(tree, RFPLParser.BuiltinCnContext):
            f, *gs = tree.fexprlist().getTypedRuleContexts(RFPLParser.FexprContext)
            for g in gs:
                basesz = max(basesz, self.preprocess(g))
            basesz = max(basesz, self.preprocess(f))
        elif isinstance(tree, RFPLParser.BuiltinPrContext):
            f = tree.fexpr(0)
            g = tree.fexpr(1)
            basesz = max(basesz, self.preprocess(f))
            basesz = max(basesz, self.preprocess(g))
        elif isinstance(tree, RFPLParser.BuiltinMnContext):
            f = tree.fexpr()
            basesz = max(basesz, self.preprocess(f))
        else:
            raise Exception(f'Unknown node {type(tree)}')
        return basesz
    
    def buildErrorMessage(self):
        msg = ''
        for err in self.errors:
            msg += err.toString(self.input_stream)
        return msg

    def interpret(self, line:str):
        self.errors = []
        try:
            self.input_stream = InputStream(line.strip())
            lexer = RFPLLexer(self.input_stream)
            lexer.removeErrorListeners()
            lexer.addErrorListener(ThrowingErrorListener(self))

            token_stream = CommonTokenStream(lexer)

            parser = RFPLParser(token_stream)
            parser.removeErrorListeners()
            parser.addErrorListener(ThrowingErrorListener(self))

            tree = parser.line()
            if self.errors:
                return False, self.buildErrorMessage()
            
            tree = tree.getChild(0)
            if isinstance(tree, RFPLParser.DefineContext):
                symb = tree.Symbol().getText()
                fexpr = tree.fexpr()
                basesz = self.preprocess(fexpr)
                if self.errors:
                    return False, self.buildErrorMessage()
                message = f'Function {symb} added'
                syment = self.symbol_table.search(symb)
                if syment is not None:
                    if syment.builtin:
                        return False, f'ERROR: Cannot redefine a builtin function {symb}'
                    message = f'Function {symb} redefined'
                self.symbol_table.add(
                    symbol=symb,
                    call=lambda blist, args, fexpr=fexpr: self.interpretFexpr(fexpr, blist, args),
                    basesz = basesz
                )
                return True, message
            elif isinstance(tree, RFPLParser.ExamineContext):
                result = self.interpretNexpr(tree.nexpr())
                if self.errors:
                    return False, self.buildErrorMessage()
                return True, result
            else:
                raise Exception('Unknown node {}'.format(type(tree)))
        except Exception as e:
            return False, f'CRITICAL: {traceback.format_exc()}'
