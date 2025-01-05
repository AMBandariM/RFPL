from typing import Union, List
from .RFPLParser import RFPLParser

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
        if isinstance(self.natural, list):
            return
        if self.natural == 0:
            return
        cur = self.natural
        self.natural = []
        pi = 0
        while cur > 1:
            cnt = 0
            while cur % getPrime(pi) == 0:
                cur //= getPrime(pi)
                cnt += 1
            self.natural.append(Natural(cnt))
            pi += 1
    
    def copy(self):
        if isinstance(self.natural, int):
            natural = self.natural
        else:
            natural = []
            for nat in self.natural:
                natural.append(nat.copy())
        return Natural(natural)

    def getEntry(self, ind: 'Natural'):
        if self.natural == 0:
            return Natural(0)
        ind = ind.toInt()
        self.factor()
        if ind >= len(self.natural):
            return Natural(0)
        return self.natural[ind]
        
    def setEntry(self, ind: 'Natural', nat: 'Natural'):
        if self.natural == 0:
            return Natural(0)
        result = self.copy()
        ind = ind.toInt()
        result.factor()
        while len(result.natural) <= ind:
            result.natural.append(Natural(0))
        result.natural[ind] = nat
        return result
    
    @staticmethod
    def interpret(tree: RFPLParser.NaturalContext):
        if tree.Number() is not None:
            return Natural(int(tree.Number().getText()))
        naturallist = tree.naturallist()
        nats = []
        for subtr in naturallist.getTypedRuleContexts(RFPLParser.NaturalContext):
            nats.append(Natural.interpret(subtr))
        return Natural(nats)
    
    def succ(self):
        return Natural(self.toInt() + 1)
    
    def isZero(self):
        return self.natural == 0
    
    def isOne(self):
        if isinstance(self.natural, int):
            return self.natural == 1
        return all(x.isZero() for x in self.natural)
    
    def add(self, other: 'Natural'):
        if self.isZero():
            return other
        if other.isZero():
            return self
        return Natural(self.toInt() + other.toInt())
    
    def multiply(self, other: 'Natural'):
        if self.isOne():
            return other
        if other.isOne():
            return self
        if isinstance(self.natural, int) or isinstance(other.natural, int):
            return Natural(self.toInt() * other.toInt())
        a = self.natural.copy()
        b = other.natural.copy()
        if len(a) < len(b):
            a += [Natural(0)] * (len(b) - len(a))
        elif len(b) < len(a):
            b += [Natural(0)] * (len(a) - len(b))
        return Natural(list(x.add(y) for x, y in zip(a, b)))
    
    def power(self, other: 'Natural'):
        if self.isZero():
            return Natural(0)
        if other.isZero():
            return Natural(1)
        if other.isOne():
            return self
        if isinstance(self.natural, int):
            p = other.toInt()
            return Natural(self.toInt() ** p)
        return Natural(list(x.multiply(other) for x in self.natural))
    
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
