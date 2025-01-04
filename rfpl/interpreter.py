from antlr4 import *
from dataclasses import dataclass
from typing import Callable
from antlr4.error.ErrorListener import ErrorListener
from antlr4.error.Errors import ParseCancellationException
from typing import Union, List

from .RFPLLexer import RFPLLexer
from .RFPLParser import RFPLParser

DEBUG = False
def debug(*args):
    if not DEBUG:
        return
    for arg in args:
        print(arg, end=' ')
    print()

primes = [2, 3, 5, 7]

def getPrime(i):
    if i < len(primes):
        return primes[i]
    cur = primes[-1] + 1
    while len(primes) <= i:
        isprime = True
        for div in primes:
            if div * div > cur:
                break
            if cur % div == 0:
                isprime = False
                break
        if isprime:
            primes.append(cur)
        cur += 1
    return primes[i]

class Natural:
    def __init__(self, natural: Union[int, List['Natural']]):
        self.natural: Union[int, List['Natural']] = natural
    
    def toInt(self):
        if isinstance(self.natural, int):
            return self.natural
        num = 1
        for i, ent in enumerate(self.natural):
            num *= getPrime(i) ** ent.toInt()
        return num
    
    def simplify(self):
        self.natural = self.toInt()

    def factor(self):
        if isinstance(self.natural, List['Natural']):
            return
        elif isinstance(self.natural, int):
            cur = self.natural
            self.natural = []
            pi = 0
            while cur > 0:
                cnt = 0
                while cur % getPrime(pi) == 0:
                    cur //= getPrime(pi)
                    cnt += 1
                self.natural.append(Natural(cnt))
                pi += 1
    
    def copy(self):
        if isinstance(self.natural, int):
            natural = self.natural
        elif isinstance(self.natural, List['Natural']):
            natural = []
            for nat in self.natural:
                natural.append(nat.copy())
        return Natural(natural)

    def getEnt(self, ind: 'Natural'):
        ind = ind.toInt()
        self.factor()
        if ind >= len(self.natural):
            return Natural(0)
        return self.natural[ind]
        
    def setEnt(self, ind: 'Natural', nat: 'Natural'):
        ind = ind.toInt()
        self.factor()
        while len(self.natural) <= ind:
            self.natural.append(Natural(0))
        self.natural[ind] = nat.copy()
    
    @staticmethod
    def interpret(tree: RFPLParser.NaturalContext):
        if tree.Number() is not None:
            return Natural(int(tree.Number().getText()))
        naturallist = tree.naturallist()
        nats = []
        for subtr in naturallist.getTypedRuleContexts(RFPLParser.NaturalContext):
            nats.append(Natural.interpret(subtr))
        return Natural(nats)
    
    def __repr__(self):
        if isinstance(self.natural, int):
            return 'N({})'.format(self.natural)
        subreps = []
        for ent in self.natural:
            subreps.append(ent.__repr__())
        return 'N<{}>'.format(', '.join(subreps))
    
    def __str__(self):
        if isinstance(self.natural, int):
            return '{}'.format(self.natural)
        subreps = []
        for ent in self.natural:
            subreps.append(ent.__str__())
        return '<{}>'.format(', '.join(subreps))


class Interpreter:
    @dataclass
    class FuncType:
        call: Callable
        builtin: bool = False
    def __init__(self):
        self.func_table = {
            'S': self.FuncType(call=lambda _stack, x : Natural(x[0].toInt() + 1), builtin=True),
        }

    def interpretFexpr(self, tree, stack, args):
        if not isinstance(tree, RFPLParser.FexprContext):
            raise Exception('tree must represent a fexpr, got {}'.format(type(tree)))
        tree = tree.getChild(0)
        debug('call', tree.getText(), args)
        if isinstance(tree, RFPLParser.FexprleafContext):
            baseNxt = []
            if tree.fexprlist() is not None:
                fexprlist: RFPLParser.FexprlistContext = tree.fexprlist()
                baseNxt += fexprlist.getTypedRuleContexts(RFPLParser.FexprContext)
            symb = tree.Symbol().getText()
            if symb not in self.func_table:
                raise Exception('function {} not defined'.format(symb))
            debug('subcall to', symb)
            return self.func_table[symb].call(stack + [baseNxt], args)
        elif isinstance(tree, RFPLParser.BracketContext):
            if len(stack) == 0:
                raise Exception('root function have no base argument')
            baseArgs = stack[-1]
            ind = Natural.interpret(tree.natural()).toInt()
            if ind >= len(baseArgs):
                raise Exception('not enough base arguments')
            return self.interpretFexpr(baseArgs[ind], stack[:-1], args)
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
                gres = self.interpretFexpr(g, stack, args)
                fargs.append(gres)
            return self.interpretFexpr(f, stack, fargs)
        elif isinstance(tree, RFPLParser.BuiltinPrContext):
            if len(args) == 0:
                raise Exception('not enough arguments for Pr')
            f = tree.fexpr(0)
            g = tree.fexpr(1)
            n = args[0].toInt()
            cur = self.interpretFexpr(f, stack, args[1:])
            for i in range(n):
                cur = self.interpretFexpr(g, stack, [cur, Natural(i)] + args[1:])
            return cur
        elif isinstance(tree, RFPLParser.BuiltinMnContext):
            f = tree.fexpr(0)
            args = [Natural(0)] + args
            while self.interpretFexpr(f, stack, args) > 0:
                args[0].natural += 1
            return args[0]
        else:
            raise Exception('unknown node {}'.format(type(tree)))

    def interpretNexpr(self, tree):
        if not isinstance(tree, RFPLParser.NexprContext):
            raise Exception('tree must represent a fexpr, got {}'.format(type(tree)))
        if tree.natural() is not None:
            return Natural.interpret(tree.natural())
        fexpr: RFPLParser.FexprContext = tree.fexpr()
        nexprlist: RFPLParser.NexprlistContext = tree.nexprlist()
        args = []
        for nexpr in nexprlist.getTypedRuleContexts(RFPLParser.NexprContext):
            args.append(self.interpretNexpr(nexpr))
        return self.interpretFexpr(fexpr, [], args)

    class ThrowingErrorListener(ErrorListener):
        def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
            ex = ParseCancellationException(f'line {line}: {column} {msg}')
            ex.line = line
            ex.column = column
            raise ex

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
                message = 'New Function Added'
                if symb in self.func_table:
                    message = f'Function {symb} Redefined'
                self.func_table[symb] = self.FuncType(lambda stack, args, fexpr=fexpr: self.interpretFexpr(fexpr, stack, args))
                return 'Success', message
            elif isinstance(tree, RFPLParser.ExamineContext):
                result = self.interpretNexpr(tree.nexpr())
                return 'Success', result
            else:
                raise Exception('unknown node {}'.format(type(tree)))  # I leave this one !
        except EOFError:
            return 'Goodbye', None
        except Exception as e:
            return f'ERROR: {e}', None
