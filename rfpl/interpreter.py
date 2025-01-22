import sys
import hashlib
import traceback
from antlr4 import *
from dataclasses import dataclass, field
from antlr4.error.ErrorListener import ErrorListener
from typing import Union, List, Dict, Tuple, Callable
import random
from enum import Enum
from pathlib import Path

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
class FunctionType:
    narg: int = 0
    nbase: int = 0
    max_narg_b: Dict = field(default_factory=dict)
    relative_narg_b: Dict = field(default_factory=dict)

    # narg is the minimum number of argument this function needs, without considering bases.
    # nbase is the number of base arguments (@0, @1, ...) this function uses.
    # @i.narg <= max_narg_b[i]
    # narg >= @i.narg + relative_narg_b[i]
    # The dictionaries may not have a value for i, indicating @i is not mentioned in the function.
    # Every fexpr has a type.


def dict_min_eq(d: dict, k, v):
    if k not in d:
        d[k] = v
    else:
        d[k] = min(d[k], v)

def dict_max_eq(d: dict, k, v):
    if k not in d:
        d[k] = v
    else:
        d[k] = max(d[k], v)


@dataclass
class SymbolEntry:
    symbol: str
    call: Callable[[BaseList, NaturalList], Natural]
    builtin: bool = False
    ix: int = -1
    ftype: FunctionType = field(default_factory=FunctionType)


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
    
    def add_entry(self, entry: SymbolEntry):
        entry.ix = len(self.table)
        self.table.append(entry)
    
    def add(self, *args, **kwargs):
        return self.add_entry(SymbolEntry(*args, **kwargs))


class HashCache:
    CACHE = False

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
            if not arg.is_zero():
                started = True
            if started:
                lst += arg.weird_hash() + '+'
        return hashlib.md5(lst.encode()).hexdigest()

    def make_mock_natural_list(self, n: int):
        m = int(n**0.5)
        a, b, c = random.randint(0,m), random.randint(0,m), random.randint(0,m)
        return NaturalList([Natural(a), Natural(b), Natural(c), Natural(None), Natural(None)])

    def call_and_cache(self, fun: SymbolEntry, blist: BaseList, args: List[Natural]):
        if (blist is not None and len(blist.args)) or fun.builtin or not self.CACHE:
            return fun.call(blist, args)
        if fun.ix not in self.possibleMatches:
            self.possibleMatches[fun.ix] = self.basic_functions.copy()
            self.counter[fun.ix] = 0
            self.cache[fun.ix] = {}
        if self.counter[fun.ix] == self.counter_max:
            return self.possibleMatches[fun.ix][0].call(blist, args)
        hsh = self.hash(args)
        if hsh in self.cache[fun.ix]:
            return self.cache[fun.ix][hsh]
        res = fun.call(blist, args)
        if self.possibleMatches[fun.ix]:
            reshsh = res.weird_hash()
            resnat = res.to_int()
            for ent in self.possibleMatches[fun.ix]:
                rel = ent.call(blist, args)
                if rel.weirdHash() != reshsh and rel.toInt() != resnat:
                    self.possibleMatches[fun.ix].remove(ent)
            mocknatlst = self.make_mock_natural_list(self.counter[fun.ix])
            rez = fun.call(None, mocknatlst)
            for ent in self.possibleMatches[fun.ix]:
                rel = ent.call(None, mocknatlst)
                if rel.weirdHash() != rez.weird_hash() and rel.toInt() != rez.to_int():
                    self.possibleMatches[fun.ix].remove(ent)
            if len(self.possibleMatches[fun.ix]):
                self.counter[fun.ix] += 1
                if self.counter[fun.ix] == self.counter_max:
                    debug(f'replacing {fun.symbol} with {self.possibleMatches[fun.ix][0].symbol} ...')
        self.cache[fun.ix][hsh] = res
        return res


class MessageType(Enum):
    INFO = 0
    NATURAL = 1
    ERROR = 2
    EXCEPTION = 3


@dataclass
class Message:
    typ: MessageType
    message: str = None
    context: List[str] = None
    natural: Natural = None
    start: int = None
    stop: int = None

    @classmethod
    def error(cls, message: str, **kwargs):
        return cls(typ=MessageType.ERROR, message=message, **kwargs)

    @classmethod
    def error_context(cls, message: str, ctx: Union[ParserRuleContext, Token]):
        result = cls.error(message)
        if isinstance(ctx, ParserRuleContext):
            result.start = ctx.start.start
            result.stop = ctx.stop.stop
        else:
            result.start = ctx.start
            result.stop = ctx.stop
        return result
    
    @classmethod
    def info(cls, message: str, **kwargs):
        return cls(typ=MessageType.INFO, message=message, *kwargs)
    
    @classmethod
    def natural(cls, nat: Natural, **kwargs):
        return cls(typ=MessageType.NATURAL, natural=nat, **kwargs)

    def add_context(self, inp: str):
        if (self.start is None or self.stop is None 
            or inp is None or self.context is not None):
            return
        self.context = [
            inp,
            ' ' * self.start + '^' + '~' * max(0, self.stop - self.start)
        ]


class ReportErrorListener(ErrorListener):
    def __init__(self, interpreter: 'Interpreter'):
        self.interpreter = interpreter

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.interpreter.add_message(Message.error_context(msg, offendingSymbol))


class QuietErrorListener(ErrorListener):
    def __init__(self):
        super().__init__()
        self.has_unexpected_eof = False

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        if offendingSymbol and offendingSymbol.type == Token.EOF:
            self.has_unexpected_eof = True


class Interpreter:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.symbol_table.add(
            symbol='S', 
            call=lambda _blist, args : args[0].succ(), 
            builtin=True,
            ftype=FunctionType(narg=1),
        )
        
        def _get_entry(_blist, args):
            if args[1].is_zero():
                return Natural(0)
            return args[1].get_entry(args[0])
        
        def _set_entry(_blist, args):
            if args[2].is_zero():
                return Natural(0)
            return args[2].set_entry(args[0], args[1])
        
        def _int(_blist, args):
            args[0].simplify()
            return args[0]
        
        def _list(_blist, args):
            if args[0].is_defined() and not args[0].is_zero():
                args[0].factor()
            return args[0]
        
        self.builtin_functions = {
            "Add": SymbolEntry(
                symbol='Add',
                call=lambda _blist, args : args[0] + args[1],
                builtin=True,
                ftype=FunctionType(narg=2),
            ),
            "Sub": SymbolEntry(
                symbol='Sub',
                call=lambda _blist, args : args[1] - args[0],
                builtin=True,
                ftype=FunctionType(narg=2),
            ),
            "Mul": SymbolEntry(
                symbol='Mul',
                call=lambda _blist, args : args[0] * args[1],
                builtin=True,
                ftype=FunctionType(narg=2),
            ),
            "Pow": SymbolEntry(
                symbol='Pow',
                call=lambda _blist, args : args[1] ** args[0],
                builtin=True,
                ftype=FunctionType(narg=2),
            ),
            "Get": SymbolEntry(
                symbol='Get',
                call=_get_entry,
                builtin=True,
                ftype=FunctionType(narg=2),
            ),
            "Set": SymbolEntry(
                symbol='Set',
                call=_set_entry,
                builtin=True,
                ftype=FunctionType(narg=3),
            ),
            "Int": SymbolEntry(
                symbol='Int',
                call=_int,
                builtin=True,
                ftype=FunctionType(narg=1),
            ),
            "List": SymbolEntry(
                symbol='List',
                call=_list,
                builtin=True,
                ftype=FunctionType(narg=1),
            ),
            "Mod": SymbolEntry(
                symbol='Mod',
                call=lambda _blist, args : args[0] % args[1],
                builtin=True,
                ftype=FunctionType(narg=2),
            ),
        }
        self.basic_arithmetic_enteries = []
        self.basic_sequential_enteries = []
        self.basic_numbertheory_enteries = []
        self.cache = HashCache(
            [self.builtin_functions[name] for name in ["Add", "Sub", "Mul", "Pow", "Get", "Set", "Mod"]]
        )
        self.messages: List[Message] = []
        self.has_error = False

    def add_message(self, msg: Message):
        self.messages.append(msg)
        if msg.typ in (MessageType.ERROR, MessageType.EXCEPTION):
            self.has_error = True

    def load_names(self, names: List[str]):
        for name in names:
            self.symbol_table.add_entry(self.builtin_functions[name])

    def load_basics(self):
        names = self.builtin_functions.keys()
        self.load_names(names)
        return names

    def interpret_fexpr(self, tree, blist: BaseList, args: NaturalList) -> Natural:
        tree = tree.getChild(0)
        if isinstance(tree, RFPLParser.FexprleafContext):
            bnxt = None
            if tree.fexprlist() is not None:
                bnxt = BaseList([], None)
                bnxt.args = tree.fexprlist().getTypedRuleContexts(RFPLParser.FexprContext)
                for bexpr in bnxt.args:
                    if bexpr.c_ftype.nbase > 0:
                        bnxt.prev = blist
                        break
            syment = tree.c_syment
            return self.cache.call_and_cache(syment, bnxt, args)
        elif isinstance(tree, RFPLParser.BracketContext):
            return self.interpret_fexpr(blist.args[tree.c_number], blist.prev, args)
        elif isinstance(tree, RFPLParser.IdentityContext):
            return args[tree.c_number]
        elif isinstance(tree, RFPLParser.ConstantContext):
            return tree.c_natural
        elif isinstance(tree, RFPLParser.BuiltinCnContext):
            f, *gs = tree.fexprlist().getTypedRuleContexts(RFPLParser.FexprContext)
            fargs = []
            for g in gs:
                gres = self.interpret_fexpr(g, blist, args)
                fargs.append(gres)
            fargs = NaturalList(fargs)
            return self.interpret_fexpr(f, blist, fargs)
        elif isinstance(tree, RFPLParser.BuiltinPrContext):
            f = tree.fexpr(0)
            g = tree.fexpr(1)
            n = args[0].to_int()
            args = args.drop(1)
            cur = self.interpret_fexpr(f, blist, args)
            args = NaturalList([Natural(None), Natural(None)]) + args
            for i in range(n):
                args[0] = cur
                args[1] = Natural(i)
                cur = self.interpret_fexpr(g, blist, args)
            return cur
        elif isinstance(tree, RFPLParser.BuiltinMnContext):
            f = tree.fexpr()
            args = NaturalList([Natural(0)]) + args
            result = self.interpret_fexpr(f, blist, args)
            while result.is_defined() and not result.is_zero():
                args[0] = args[0].succ()
                result = self.interpret_fexpr(f, blist, args)
            if not result.is_defined():
                return Natural(None)
            return args[0]

    def interpret_nexpr(self, tree):
        if not isinstance(tree, RFPLParser.NexprContext):
            raise Exception('Tree must represent a nexpr, got {}'.format(type(tree)))
        if tree.natural() is not None:
            return Natural.interpret(tree.natural())
        fexpr: RFPLParser.FexprContext = tree.fexpr()
        nexprlist: RFPLParser.NexprlistContext = tree.nexprlist()
        args = []
        for nexpr in nexprlist.getTypedRuleContexts(RFPLParser.NexprContext):
            args.append(self.interpret_nexpr(nexpr))
        ftype = self.preprocess(fexpr)
        if ftype.nbase > 0:
            self.add_message(Message.error_context(
                f'Function should not need any bases',
                tree,
            ))
        elif ftype.narg > len(args):
            self.add_message(Message.error_context(
                f'Function expects {ftype.narg} arguments but got {len(args)}',
                tree,
            ))
        if self.has_error:
            return Natural(None)
        args = NaturalList(args)
        return self.interpret_fexpr(fexpr, None, args)

    def preprocess(self, root) -> FunctionType:
        # to have consistent variable names, we will call the current tree as f
        ftype = FunctionType()

        tree = root.getChild(0)
        if isinstance(tree, RFPLParser.FexprleafContext):
            # assume f = g[gb0, gb1, ...]
            gbase = []
            if tree.fexprlist() is not None:
                fexprlist: RFPLParser.FexprlistContext = tree.fexprlist()
                gbase += fexprlist.getTypedRuleContexts(RFPLParser.FexprContext)
            symb = tree.Symbol().getText()
            syment = self.symbol_table.search(symb)
            if syment is None:
                self.add_message(Message.error_context(f'Function {symb} is not defined', tree))
                return ftype
            gtype = syment.ftype
            if len(gbase) != gtype.nbase:
                self.add_message(Message.error_context(
                    f'Function {symb} accepts {gtype.nbase} bases but got {len(gbase)}',
                    tree,
                ))
                return ftype
            tree.c_syment = syment  # custom attribute added to the tree
            ftype.narg = max(ftype.narg, gtype.narg)
            for gi, gb in enumerate(gbase):
                gbtype = self.preprocess(gb)
                ftype.nbase = max(ftype.nbase, gbtype.nbase)
                if gi in gtype.max_narg_b:
                    if gbtype.narg > gtype.max_narg_b[gi]:
                        self.add_message(Message.error_context(
                            f'Base @{gi} of function {syment.symbol} '
                            f'needs {gbtype.narg} arguments, but is limited to at most '
                            f'{gtype.max_narg_b[gi]} arguments by function {syment.symbol}',
                            tree,
                        ))
                        return ftype
                    for fj in gbtype.relative_narg_b:
                        dict_min_eq(ftype.max_narg_b, fj, gtype.max_narg_b[gi] - gbtype.relative_narg_b[fj])
                        if ftype.max_narg_b[fj] < 0:
                            self.add_message(Message.error_context(
                                f'Base @{gi} of function {syment.symbol} is abusing base @{fj} of caller function',
                                tree,
                            ))
                            return ftype
                if gi in gtype.relative_narg_b:
                    ftype.narg = max(ftype.narg, gtype.relative_narg_b[gi] + gbtype.narg)
                    for fj in gbtype.relative_narg_b:
                        dict_max_eq(ftype.relative_narg_b, fj, gtype.relative_narg_b[gi] + gbtype.relative_narg_b[fj])
                for fj in gbtype.max_narg_b:
                    dict_min_eq(ftype.max_narg_b, fj, gbtype.max_narg_b[fj])

        elif isinstance(tree, RFPLParser.BracketContext):
            ix = int(tree.Number().getText())
            tree.c_number = ix
            ftype.relative_narg_b[ix] = 0
            ftype.nbase = ix + 1

        elif isinstance(tree, RFPLParser.IdentityContext):
            ix = int(tree.Number().getText())
            tree.c_number = ix
            ftype.narg = ix + 1

        elif isinstance(tree, RFPLParser.ConstantContext):
            tree.c_natural = Natural.interpret(tree.natural())

        elif isinstance(tree, RFPLParser.BuiltinCnContext):
            # assume f = h[g0, g1, ...]
            h, *gs = tree.fexprlist().getTypedRuleContexts(RFPLParser.FexprContext)
            htype = self.preprocess(h)
            for fj in htype.max_narg_b:
                ftype.max_narg_b[fj] = htype.max_narg_b[fj]
            ftype.nbase = htype.nbase

            ngs = len(gs)
            if ngs < htype.narg:
                self.add_message(Message.error_context(
                    f'Function needs at least {htype.narg} arguments but got {ngs}',
                    h,
                ))
                return ftype
            
            for fj in htype.relative_narg_b:
                dict_min_eq(ftype.max_narg_b, fj, ngs - htype.relative_narg_b[fj])
                if ftype.max_narg_b[fj] < 0:
                    self.add_message(Message.error_context(
                        f'Function is abusing base @{fj}',  ## I don't know what to say!
                        h,
                    ))
                    return ftype
            
            for g in gs:
                gtype = self.preprocess(g)
                ftype.narg = max(ftype.narg, gtype.narg)
                ftype.nbase = max(ftype.nbase, gtype.nbase)
                for fj in gtype.relative_narg_b:
                    dict_max_eq(ftype.relative_narg_b, fj, gtype.relative_narg_b[fj])
                for fj in gtype.max_narg_b:
                    dict_min_eq(ftype.max_narg_b, fj, gtype.max_narg_b[fj])
            
        elif isinstance(tree, RFPLParser.BuiltinPrContext):
            # assume f = Pr[h, g]
            h = tree.fexpr(0)
            g = tree.fexpr(1)
            htype = self.preprocess(h)
            ftype.narg = htype.narg + 1
            ftype.nbase = htype.nbase
            for fj in htype.relative_narg_b:
                dict_max_eq(ftype.relative_narg_b, fj, htype.relative_narg_b[fj] + 1)
            for fj in htype.max_narg_b:
                dict_min_eq(ftype.max_narg_b, fj, htype.max_narg_b[fj])

            gtype = self.preprocess(g)
            ftype.narg = max(ftype.narg, gtype.narg - 1)
            ftype.nbase = max(ftype.nbase, gtype.nbase)
            for fj in gtype.relative_narg_b:
                dict_max_eq(ftype.relative_narg_b, fj, gtype.relative_narg_b[fj] - 1)
            for fj in gtype.max_narg_b:
                dict_min_eq(ftype.max_narg_b, fj, gtype.max_narg_b[fj])

        elif isinstance(tree, RFPLParser.BuiltinMnContext):
            # assume f = Mn[h]
            h = tree.fexpr()
            htype = self.preprocess(h)
            ftype.narg = max(ftype.narg, htype.narg - 1)
            ftype.nbase = htype.nbase
            for fj in htype.relative_narg_b:
                dict_max_eq(ftype.relative_narg_b, fj, htype.relative_narg_b[fj] - 1)
            for fj in htype.max_narg_b:
                dict_min_eq(ftype.max_narg_b, fj, htype.max_narg_b[fj])
    
        else:
            raise Exception(f'Unknown node {type(tree)}')

        root.c_ftype = ftype
        return ftype
    
    def interpret(self, line: str) -> bool:
        self.has_error = False

        input_stream = InputStream(line)
        lexer = RFPLLexer(input_stream)
        lexer.removeErrorListeners()
        lexer.addErrorListener(ReportErrorListener(self))

        token_stream = CommonTokenStream(lexer)

        parser = RFPLParser(token_stream)
        parser.removeErrorListeners()
        parser.addErrorListener(ReportErrorListener(self))

        tree = parser.singleline()
        if self.has_error:
            return False

        tree = tree.line()
        if tree is None:
            return True, None
        elif tree.define() is not None:
            tree = tree.define()
            symb = tree.Symbol().getText()
            fexpr = tree.fexpr()
            ftype = self.preprocess(fexpr)
            if self.has_error:
                return False
            msg = Message.info(f'Function {symb} added')
            syment = self.symbol_table.search(symb)
            if syment is not None:
                if syment.builtin:
                    self.add_message(Message.error_context(
                        f'Cannot redefine a builtin function {symb}',
                        tree.Symbol()
                    ))
                    return False
                msg.message = f'Function {symb} redefined'
            self.symbol_table.add(
                symbol=symb,
                call=lambda blist, args, fexpr=fexpr: self.interpret_fexpr(fexpr, blist, args),
                ftype=ftype,
            )
            self.add_message(msg)
            return True
        elif tree.examine() is not None:
            tree = tree.examine()
            result = self.interpret_nexpr(tree.nexpr())
            if self.has_error:
                return False
            self.add_message(Message.natural(result))
            return True
        elif tree.pragma() is not None:
            tree = tree.pragma()
            if tree.load() is not None:
                tree = tree.load()
                return self.load_module(tree.module().getText())
            else:
                raise Exception(f'Unknown pragma {tree.getText()}')
        else:
            raise Exception(f'Unknown tree type {tree.getText()}')
        
    def parsable(self, text: str):
        input_stream = InputStream(text)
        lexer = RFPLLexer(input_stream)
        stream = CommonTokenStream(lexer)
        parser = RFPLParser(stream)
        error_listener = QuietErrorListener()
        lexer.removeErrorListeners()
        lexer.addErrorListener(error_listener)
        parser.removeErrorListeners()
        parser.addErrorListener(error_listener)
        tree = parser.singleline()
        return not error_listener.has_unexpected_eof, tree
        
    def load_module(self, module: str) -> bool:
        if module == 'basics':
            names = self.load_basics()
            self.add_message(Message.info(
                'Basic functions added: ' + ', '.join(names)
            ))
            return True
        path = Path('.')
        for part in module.split('.'):
            path = path / part
        try:
            file = open(path, 'r')
        except OSError as e:
            try:
                path = path.with_suffix('.rfpl')
                file = open(path, 'r')
            except OSError as e:
                self.add_message(Message.error(f'Unable to open "{path}": ' + e.strerror))
                return False
        ok = True
        with file:
            lines = file.readlines()
            cmd = ''
            for line in lines:
                cmd += line.strip() + ' '
                if not self.parsable(cmd)[0]:
                    continue
                cmdok, _ = self.report(cmd, clear=False)
                if not cmdok:
                    ok = False
                cmd = ''
        self.add_message(Message.info(
            f'File "{path}" loaded'
        ))
        return ok

    def report(self, line: str, clear: bool = True) -> Tuple[bool, List[Message]]:
        line = line.strip()
        try:
            ok = self.interpret(line)
        except Exception:
            self.messages.append(Message(
                typ=MessageType.EXCEPTION,
                message=traceback.format_exc().strip()
            ))
            ok = False
        for msg in self.messages:
            msg.add_context(line)
        if clear:
            result = self.messages.copy()
            self.messages = []
            return ok, result
        return ok, self.messages
