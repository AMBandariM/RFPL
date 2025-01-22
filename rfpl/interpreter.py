import sys
import hashlib
import traceback
from antlr4 import *
from dataclasses import dataclass, field
from antlr4.error.ErrorListener import ErrorListener
from antlr4.error.Errors import ParseCancellationException
from typing import Union, List, Dict, Tuple, Callable
import random
from enum import Enum

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
    
    def addEntry(self, entry: SymbolEntry):
        entry.ix = len(self.table)
        self.table.append(entry)
    
    def add(self, *args, **kwargs):
        return self.addEntry(SymbolEntry(*args, **kwargs))


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
            if not arg.isZero():
                started = True
            if started:
                lst += arg.weirdHash() + '+'
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
        if hsh in self.cache[fun.ix]:
            return self.cache[fun.ix][hsh]
        res = fun.call(blist, args)
        if self.possibleMatches[fun.ix]:
            reshsh = res.weirdHash()
            resnat = res.toInt()
            for ent in self.possibleMatches[fun.ix]:
                rel = ent.call(blist, args)
                if rel.weirdHash() != reshsh and rel.toInt() != resnat:
                    self.possibleMatches[fun.ix].remove(ent)
            mocknatlst = self.makeMockNaturalList(self.counter[fun.ix])
            rez = fun.call(None, mocknatlst)
            for ent in self.possibleMatches[fun.ix]:
                rel = ent.call(None, mocknatlst)
                if rel.weirdHash() != rez.weirdHash() and rel.toInt() != rez.toInt():
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
    def errorContext(cls, message: str, ctx: Union[ParserRuleContext, Token]):
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

    def addContext(self, inp: str):
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
        self.interpreter.addMessage(Message.errorContext(msg, offendingSymbol))


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
        
        self.allBuitinFunctions = {
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
                call=_getEntry,
                builtin=True,
                nargs=2
            ),
            "Set": SymbolEntry(
                symbol='Set',
                call=_setEntry,
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
            [self.allBuitinFunctions[name] for name in ["Add", "Sub", "Mul", "Pow", "Get", "Set", "Mod"]]
        )
        self.messages: List[Message] = []
        self.has_error = False

    def addMessage(self, msg: Message):
        self.messages.append(msg)
        if msg.typ in (MessageType.ERROR, MessageType.EXCEPTION):
            self.has_error = True

    def loadList(self, names: List[str]):
        for name in names:
            self.symbol_table.addEntry(self.allBuitinFunctions[name])

    def loadBasics(self):
        names = [name for name in self.allBuitinFunctions]
        self.loadList(names)
        return names

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
            result = self.interpretFexpr(f, blist, args)
            while result.isDefined() and not result.isZero():
                args[0] = args[0].succ()
                result = self.interpretFexpr(f, blist, args)
            if not result.isDefined():
                return Natural(None)
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
        bs, na, _, _ = self.preprocess(fexpr)
        if bs > 0:
            self.addMessage(Message.errorContext(
                f'the function shouldn\'t need any bases!',
                tree,
            ))
        elif na > len(args):
            self.addMessage(Message.errorContext(
                f'the function expects {na} arguments but got {len(args)}',
                tree,
            ))
        if self.has_error:
            return Natural(None)
        args = NaturalList(args)
        return self.interpretFexpr(fexpr, None, args)

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
                self.addMessage(Message.errorContext(f'Function {symb} is not defined', tree))
                return basesz, nargs, nargs_base_dependencies, max_narg_for_base
            if len(base_nxt) != syment.basesz:
                self.addMessage(Message.errorContext(
                    f'Function {symb} accepts {syment.basesz} bases but got {len(base_nxt)}',
                    tree,
                ))
                return basesz, nargs, nargs_base_dependencies, max_narg_for_base
            # tree.children.append(syment)     ## so, do we need this? TODO 
            tree.c_syment = syment  # custom attribute added to the tree
            nargs = max(nargs, syment.nargs)
            for i, b in enumerate(base_nxt):
                bs, na, nabd, mnab = self.preprocess(b)
                if i in syment.max_narg_for_base.keys():
                    if na > syment.max_narg_for_base[i]:
                        self.addMessage(Message.errorContext(
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
                            self.addMessage(Message.errorContext(
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
                self.addMessage(Message.errorContext(
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
                    self.addMessage(Message.errorContext(
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
    
    def interpretString(self, text: str):
        return text[1:-1].replace('\\\\', '\\').replace('\\"', '"').replace('\\\'', '\'')
    
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
                    self.addMessage(Message.errorContext(
                        f'Cannot redefine a builtin function {symb}',
                        tree.Symbol()
                    ))
                    return False
                msg.message = f'Function {symb} redefined'
            self.symbol_table.add(
                symbol=symb,
                call=lambda blist, args, fexpr=fexpr: self.interpretFexpr(fexpr, blist, args),
                basesz = basesz,
                nargs = nargs,
                nargs_base_dependencies = nargs_base_dependencies,
                max_narg_for_base = max_narg_for_base
            )
            self.addMessage(msg)
            return True
        elif tree.examine() is not None:
            tree = tree.examine()
            result = self.interpretNexpr(tree.nexpr())
            if self.has_error:
                return False
            self.addMessage(Message.natural(result))
            return True
        elif tree.pragma() is not None:
            tree = tree.pragma()
            if tree.load() is not None:
                tree = tree.load()
                filename = self.interpretString(tree.String().getText())
                return self.loadFile(filename)
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
        
    def loadFile(self, filename: str) -> bool:
        if filename == 'basics':
            names = self.loadBasics()
            self.addMessage(Message.info(
                'Basic functions added: ' + ', '.join(names)
            ))
            return True 
        try:
            file = open(filename, 'r')
        except OSError as e:
            try:
                file = open(filename + '.rfpl', 'r')
                filename += '.rfpl'
            except OSError as e:
                self.addMessage(Message.error(f'Unable to open "{filename}": ' + e.strerror))
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
        self.addMessage(Message.info(
            f'File "{filename}" loaded'
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
            msg.addContext(line)
        if clear:
            result = self.messages.copy()
            self.messages = []
            return ok, result
        return ok, self.messages
