from antlr4 import *
from rfplLexer import rfplLexer
from rfplParser import rfplParser
from dataclasses import dataclass
from typing import Callable
from antlr4.error.ErrorListener import ErrorListener
from antlr4.error.Errors import ParseCancellationException
from copy import deepcopy


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
    def __init__(self, natural: int | list):
        self.natural = natural
    
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
        if isinstance(self.natural, list):
            return
        cur = self.natural
        self.natural = []
        pi = 0
        while cur > 0:
            cnt = 0
            while cur % getPrime(pi) == 0:
                cur //= getPrime(pi)
                cnt += 1
            self.natural.append(cnt)
            pi += 1
    
    def copy(self):
        return Natural(self.natural)

    def getEnt(self, ind):
        ind = ind.toInt()
        self.factor()
        if ind >= len(self.natural):
            return Natural(0)
        return self.natural[ind]
        
    def setEnt(self, ind, nat):
        ind = ind.toInt()
        self.factor()
        while len(self.natural) <= ind:
            self.natural.append(Natural(0))
        self.natural[ind] = nat
    
    @staticmethod
    def interpret(tree: rfplParser.NaturalContext):
        if tree.Number() is not None:
            return Natural(int(tree.Number().getText()))
        naturallist = tree.naturallist()
        nats = []
        for subtr in naturallist.getTypedRuleContexts(rfplParser.NaturalContext):
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
    
@dataclass
class FuncType:
    call: Callable
    builtin: bool = False


func_table = {
    'S': FuncType(call=lambda _stack, x : Natural(x[0].toInt() + 1), builtin=True),
}

def interpretFexpr(tree, stack, args):
    if not isinstance(tree, rfplParser.FexprContext):
        raise Exception('tree must represent a fexpr, got {}'.format(type(tree)))
    tree = tree.getChild(0)
    print('call', tree.getText(), args)
    if isinstance(tree, rfplParser.FexprleafContext):
        baseNxt = []
        if tree.fexprlist() is not None:
            fexprlist: rfplParser.FexprlistContext = tree.fexprlist()
            baseNxt += fexprlist.getTypedRuleContexts(rfplParser.FexprContext)
        symb = tree.Symbol().getText()
        if symb not in func_table:
            raise Exception('function {} not defined'.format(symb))
        print('subcall to', symb)
        return func_table[symb].call(stack + [baseNxt], args)
    elif isinstance(tree, rfplParser.BracketContext):
        if len(stack) == 0:
            raise Exception('root function have no base argument')
        baseArgs = stack[-1]
        ind = Natural.interpret(tree.natural()).toInt()
        if ind >= len(baseArgs):
            raise Exception('not enough base arguments')
        return interpretFexpr(baseArgs[ind], stack[:-1], args)
    elif isinstance(tree, rfplParser.IdentityContext):
        ind = Natural.interpret(tree.natural()).toInt()
        print(ind, args)
        if ind >= len(args):
            raise Exception('not enough arguments')
        return args[ind]
    elif isinstance(tree, rfplParser.ConstantContext):
        return Natural.interpret(tree.natural())
    elif isinstance(tree, rfplParser.BuiltinCnContext):
        f, *gs = tree.fexprlist().getTypedRuleContexts(rfplParser.FexprContext)
        fargs = []
        for g in gs:
            gres = interpretFexpr(g, stack, args)
            fargs.append(gres)
        return interpretFexpr(f, stack, fargs)
    elif isinstance(tree, rfplParser.BuiltinPrContext):
        if len(args) == 0:
            raise Exception('not enough arguments for Pr')
        f = tree.fexpr(0)
        g = tree.fexpr(1)
        n = args[0].toInt()
        cur = interpretFexpr(f, stack, args[1:])
        for i in range(1, n+1):
            cur = interpretFexpr(g, stack, [Natural(i), cur] + args[1:])
        return cur
    elif isinstance(tree, rfplParser.BuiltinMnContext):
        f = tree.fexpr(0)
        args = [Natural(0)] + args
        while interpretFexpr(f, stack, args) > 0:
            args[0].natural += 1
        return args[0]
    else:
        raise Exception('unknown node {}'.format(type(tree)))


def interpretNexpr(tree):
    if not isinstance(tree, rfplParser.NexprContext):
        raise Exception('tree must represent a fexpr, got {}'.format(type(tree)))
    if tree.natural() is not None:
        return Natural.interpret(tree.natural())
    fexpr: rfplParser.FexprContext = tree.fexpr()
    nexprlist: rfplParser.NexprlistContext = tree.nexprlist()
    args = []
    for nexpr in nexprlist.getTypedRuleContexts(rfplParser.NexprContext):
        args.append(interpretNexpr(nexpr))
    return interpretFexpr(fexpr, [], args)


class ThrowingErrorListener(ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        ex = ParseCancellationException(f'line {line}: {column} {msg}')
        ex.line = line
        ex.column = column
        raise ex


while True:
    try:
        input_stream = InputStream(input(">> ").strip())
        lexer = rfplLexer(input_stream)
        lexer.removeErrorListeners()
        lexer.addErrorListener(ThrowingErrorListener())

        token_stream = CommonTokenStream(lexer)\

        parser = rfplParser(token_stream)
        parser.removeErrorListeners()
        parser.addErrorListener(ThrowingErrorListener())

        tree = parser.line()
        # print("parse Tree:")
        # print(tree.toStringTree(recog=parser))  # Display the parse tree

        tree = tree.getChild(0)
        if isinstance(tree, rfplParser.DefineContext):
            symb = tree.Symbol().getText()
            fexpr = tree.fexpr()
            if symb in func_table:
                print('redefine function {}'.format(symb))
            func_table[symb] = FuncType(lambda stack, args: interpretFexpr(fexpr, stack, args))
        elif isinstance(tree, rfplParser.ExamineContext):
            result = interpretNexpr(tree.nexpr())
            print(result)
        else:
            raise Exception('unknown node {}'.format(type(tree)))
    except EOFError:
        print('\nGoodbye')
        break
    except Exception as e:
        print('ERROR:', e)
