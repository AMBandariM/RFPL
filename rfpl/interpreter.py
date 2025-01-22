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
class SymbolEntry:
    symbol: str
    call: Callable[[BaseList, NaturalList], Natural]
    builtin: bool = False
    ix: int = -1
    basesz: int = 0
    nargs: int = 0
    nargs_base_dependencies: Dict = field(default_factory=dict)
    max_narg_for_base: Dict = field(default_factory=dict)


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
            nargs=1
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
                nargs=2
            ),
            "Sub": SymbolEntry(
                symbol='Sub',
                call=lambda _blist, args : args[1] - args[0],
                builtin=True,
                nargs=2
            ),
            "Mul": SymbolEntry(
                symbol='Mul',
                call=lambda _blist, args : args[0] * args[1],
                builtin=True,
                nargs=2
            ),
            "Pow": SymbolEntry(
                symbol='Pow',
                call=lambda _blist, args : args[1] ** args[0],
                builtin=True,
                nargs=2
            ),
            "Get": SymbolEntry(
                symbol='Get',
                call=_get_entry,
                builtin=True,
                nargs=2
            ),
            "Set": SymbolEntry(
                symbol='Set',
                call=_set_entry,
                builtin=True,
                nargs=3
            ),
            "Int": SymbolEntry(
                symbol='Int',
                call=_int,
                builtin=True,
                nargs=1
            ),
            "List": SymbolEntry(
                symbol='List',
                call=_list,
                builtin=True,
                nargs=1
            ),
            "Mod": SymbolEntry(
                symbol='Mod',
                call=lambda _blist, args : args[0] % args[1],
                builtin=True
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
            base_nxt = []
            if tree.fexprlist() is not None:
                fexprlist: RFPLParser.FexprlistContext = tree.fexprlist()
                base_nxt += fexprlist.getTypedRuleContexts(RFPLParser.FexprContext)
            syment = tree.c_syment
            return self.cache.call_and_cache(syment, BaseList(base_nxt, blist), args)
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
        bs, na, _, _ = self.preprocess(fexpr)
        if bs > 0:
            self.add_message(Message.error_context(
                f'the function shouldn\'t need any bases!',
                tree,
            ))
        elif na > len(args):
            self.add_message(Message.error_context(
                f'the function expects {na} arguments but got {len(args)}',
                tree,
            ))
        if self.has_error:
            return Natural(None)
        args = NaturalList(args)
        return self.interpret_fexpr(fexpr, None, args)

    def preprocess(self, tree):
        basesz = 0
        nargs = 0
        nargs_base_dependencies = {}
        max_narg_for_base = {}   ## for example, Cn[@0,#0] indicates that @0 shouldn't need more than one arguments! 

        tree = tree.getChild(0)
        if isinstance(tree, RFPLParser.FexprleafContext):
            base_nxt = []
            if tree.fexprlist() is not None:
                fexprlist: RFPLParser.FexprlistContext = tree.fexprlist()
                base_nxt += fexprlist.getTypedRuleContexts(RFPLParser.FexprContext)
            symb = tree.Symbol().getText()
            syment = self.symbol_table.search(symb)
            if syment is None:
                self.add_message(Message.error_context(f'Function {symb} is not defined', tree))
                return basesz, nargs, nargs_base_dependencies, max_narg_for_base
            if len(base_nxt) != syment.basesz:
                self.add_message(Message.error_context(
                    f'Function {symb} accepts {syment.basesz} bases but got {len(base_nxt)}',
                    tree,
                ))
                return basesz, nargs, nargs_base_dependencies, max_narg_for_base
            tree.c_syment = syment  # custom attribute added to the tree
            nargs = max(nargs, syment.nargs)
            for i, b in enumerate(base_nxt):
                bs, na, nabd, mnab = self.preprocess(b)
                if i in syment.max_narg_for_base.keys():
                    if na > syment.max_narg_for_base[i]:
                        self.add_message(Message.error_context(
                            f'Base no. {i+1} of function {syment.symbol} should get at most {syment.max_narg_for_base[i]} ' + 
                            f'arguments but got {na}',
                            tree,
                        ))
                        return basesz, nargs, nargs_base_dependencies, max_narg_for_base
                    for j in nabd.keys():
                        if j in max_narg_for_base.keys():
                            max_narg_for_base[j] = min(max_narg_for_base[j], syment.max_narg_for_base[i] - nabd[j])
                        else:
                            max_narg_for_base[j] = syment.max_narg_for_base[i] - nabd[j]
                        if max_narg_for_base[j] < 0:
                            self.add_message(Message.error_context(
                                f'Some contradiction happend!',  ## I don't know what to say!
                                tree,
                            ))
                            return basesz, nargs, nargs_base_dependencies, max_narg_for_base
                if i in syment.nargs_base_dependencies.keys():
                    dff = syment.nargs_base_dependencies[i]
                    nargs = max(nargs, dff + na)
                    for j in nabd.keys():
                        if j in nargs_base_dependencies.keys():
                            nargs_base_dependencies[j] = max(nargs_base_dependencies[j], dff + nabd[j])
                        else:
                            nargs_base_dependencies[j] = dff + nabd[j]
                for j in mnab.keys():
                    if j in max_narg_for_base.keys():
                        max_narg_for_base[j] = min(max_narg_for_base[j], mnab[j])
                    else:
                        max_narg_for_base[j] = mnab[j]
                basesz = max(basesz, bs)
        elif isinstance(tree, RFPLParser.BracketContext):
            tree.c_number = int(tree.Number().getText())
            nargs_base_dependencies[tree.c_number] = 0
            basesz = tree.c_number + 1
        elif isinstance(tree, RFPLParser.IdentityContext):
            tree.c_number = int(tree.Number().getText())
            nargs = tree.c_number + 1
        elif isinstance(tree, RFPLParser.ConstantContext):
            tree.c_natural = Natural.interpret(tree.natural())
        elif isinstance(tree, RFPLParser.BuiltinCnContext):
            f, *gs = tree.fexprlist().getTypedRuleContexts(RFPLParser.FexprContext)
            bs, na, nabd, mnab = self.preprocess(f)
            for i in mnab.keys():
                max_narg_for_base[i] = mnab[i]
            basesz = bs

            ngs = len(gs)
            if ngs < na:
                self.add_message(Message.error_context(
                    f'Function {f.getText()} needs at least {na} arguments but got {ngs}',
                    tree,
                ))
                return basesz, nargs, nargs_base_dependencies, max_narg_for_base
            
            for j in nabd.keys():
                if j in max_narg_for_base.keys():
                    max_narg_for_base[j] = min(max_narg_for_base[j], ngs - nabd[j])
                else:
                    max_narg_for_base[j] = ngs - nabd[j]
                if max_narg_for_base[j] < 0:
                    self.add_message(Message.error_context(
                        f'Some contradiction happend!',  ## I don't know what to say!
                        tree,
                    ))
                    return basesz, nargs, nargs_base_dependencies, max_narg_for_base
            
            for g in gs:
                bs, na, nabd, mnab = self.preprocess(g)
                nargs = max(nargs, na)
                for i in nabd.keys():
                    if i in nargs_base_dependencies.keys():
                        nargs_base_dependencies[i] = max(nargs_base_dependencies[i], nabd[i])
                    else:
                        nargs_base_dependencies[i] = nabd[i]
                for i in mnab.keys():
                    if i in max_narg_for_base.keys():
                        max_narg_for_base[i] = min(max_narg_for_base[i], mnab[i])
                    else:
                        max_narg_for_base[i] = mnab[i]
                basesz = max(basesz, bs)
            
        elif isinstance(tree, RFPLParser.BuiltinPrContext):
            f = tree.fexpr(0)
            g = tree.fexpr(1)
            bs, na, nabd, mnab = self.preprocess(f)
            nargs = max(nargs, na + 1)
            for i in nabd.keys():
                if i in nargs_base_dependencies.keys():
                    nargs_base_dependencies[i] = max(nargs_base_dependencies[i], nabd[i] + 1)
                else:
                    nargs_base_dependencies[i] = nabd[i] + 1
            for i in mnab.keys():
                if i in max_narg_for_base.keys():
                    max_narg_for_base[i] = min(max_narg_for_base[i], mnab[i])
                else:
                    max_narg_for_base[i] = mnab[i]
            basesz = max(basesz, bs)

            bs, na, nabd, mnab = self.preprocess(g)
            nargs = max(nargs, na - 1)
            for i in nabd.keys():
                if i in nargs_base_dependencies.keys():
                    nargs_base_dependencies[i] = max(nargs_base_dependencies[i], nabd[i] + 1)
                else:
                    nargs_base_dependencies[i] = nabd[i] - 1
            for i in mnab.keys():
                if i in max_narg_for_base.keys():
                    max_narg_for_base[i] = min(max_narg_for_base[i], mnab[i])
                else:
                    max_narg_for_base[i] = mnab[i]
            basesz = max(basesz, bs)

        elif isinstance(tree, RFPLParser.BuiltinMnContext):
            f = tree.fexpr()
            bs, na, nabd, mnab = self.preprocess(f)
            nargs = max(nargs, na - 1)
            for i in nabd.keys():
                if i in nargs_base_dependencies.keys():
                    nargs_base_dependencies[i] = max(nargs_base_dependencies[i], nabd[i] + 1)
                else:
                    nargs_base_dependencies[i] = nabd[i] - 1
            for i in mnab.keys():
                if i in max_narg_for_base.keys():
                    max_narg_for_base[i] = min(max_narg_for_base[i], mnab[i])
                else:
                    max_narg_for_base[i] = mnab[i]
            basesz = max(basesz, bs)
        else:
            raise Exception(f'Unknown node {type(tree)}')
        return basesz, nargs, nargs_base_dependencies, max_narg_for_base
    
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
            basesz, nargs, nargs_base_dependencies, max_narg_for_base = self.preprocess(fexpr)
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
                basesz = basesz,
                nargs = nargs,
                nargs_base_dependencies = nargs_base_dependencies,
                max_narg_for_base = max_narg_for_base
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
