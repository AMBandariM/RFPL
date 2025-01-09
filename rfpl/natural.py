from typing import Union, List
import hashlib
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
    __slots__ = ('__natural',)

    def __init__(self, natural: Union[int, List['Natural']]):
        if isinstance(natural, int) and natural < 0:
            raise Exception(f'Cannot initialize natural with negative number {natural}')
        self.__natural: Union[int, List['Natural']] = natural
    
    def isDefined(self):
        return self.__natural is not None

    def isZero(self):
        return self.__natural == 0
    
    def isOne(self):
        if isinstance(self.__natural, int):
            return self.__natural == 1
        return self.isDefined() and all(x.isZero() for x in self.__natural)
    
    def toInt(self):
        if not self.isDefined():
            return -1
        if isinstance(self.__natural, int):
            return self.__natural
        num = 1
        for i, ent in enumerate(self.__natural):
            num *= getPrime(i) ** ent.toInt()
        return num
    
    def simplify(self):
        self.__natural = self.toInt()

    def factor(self):
        if isinstance(self.__natural, list):
            return
        if self.isZero() or not self.isDefined():
            raise Exception('Zero or undefined cannot be factored')
        cur = self.__natural
        self.__natural = []
        pi = 0
        while cur > 1:
            cnt = 0
            while cur % getPrime(pi) == 0:
                cur //= getPrime(pi)
                cnt += 1
            self.__natural.append(Natural(cnt))
            pi += 1
    
    def copy(self):
        if not self.isDefined():
            return Natural(None)
        if isinstance(self.__natural, int):
            return Natural(self.__natural)
        natural = []
        for nat in self.__natural:
            natural.append(nat.copy())
        return Natural(natural)

    def getEntry(self, ind: 'Natural'):
        if not self.isDefined() or not ind.isDefined():
            return Natural(None)
        ind = ind.toInt()
        self.factor()
        if ind >= len(self.__natural):
            return Natural(0)
        return self.__natural[ind]
        
    def setEntry(self, ind: 'Natural', nat: 'Natural'):
        if not self.isDefined() or not ind.isDefined():
            return Natural(None)
        self.factor()
        result = self.copy()
        ind = ind.toInt()
        while len(result.__natural) <= ind:
            result.__natural.append(Natural(0))
        result.__natural[ind] = nat
        return result
    
    @staticmethod
    def interpret(tree: RFPLParser.NaturalContext):
        if tree.Number() is not None:
            return Natural(int(tree.Number().getText()))
        if tree.naturallist() is not None:
            naturallist = tree.naturallist()
            nats = []
            for subtr in naturallist.getTypedRuleContexts(RFPLParser.NaturalContext):
                nats.append(Natural.interpret(subtr))
            return Natural(nats)
        return Natural(None)
    
    def succ(self):
        if not self.isDefined():
            return Natural(None)
        return Natural(self.toInt() + 1)
    
    def __add__(self, other: 'Natural'):
        if not self.isDefined() or not other.isDefined():
            return Natural(None)
        return Natural(self.toInt() + other.toInt())

    def __sub__(self, other: 'Natural'):
        if not self.isDefined() or not other.isDefined():
            return Natural(None)
        return Natural(max(self.toInt() - other.toInt(), 0))
    
    def __mul__(self, other: 'Natural'):
        if not self.isDefined() or not other.isDefined():
            return Natural(None)
        if isinstance(self.__natural, int) or isinstance(other.__natural, int):
            return Natural(self.toInt() * other.toInt())
        a = self.__natural.copy()
        b = other.__natural.copy()
        if len(a) < len(b):
            a += [Natural(0)] * (len(b) - len(a))
        elif len(b) < len(a):
            b += [Natural(0)] * (len(a) - len(b))
        return Natural(list(x + y for x, y in zip(a, b)))

    def __pow__(self, other: 'Natural'):
        if not self.isDefined() or not other.isDefined():
            return Natural(None)
        if other.isZero():
            return Natural(1)
        if other.isOne():
            return Natural(self.__natural)
        if isinstance(self.__natural, int):
            p = other.toInt()
            return Natural(self.__natural ** p)
        return Natural(list(x * other for x in self.__natural))

    def __mod__(self, other: 'Natural'):
        if not self.isDefined() or not other.isDefined():
            return Natural(None)
        if other.isZero():
            return self
        return Natural(self.toInt() % other.toInt())
    
    def __repr__(self):
        if not self.isDefined():
            return 'Undefined'
        if isinstance(self.__natural, int):
            return 'N({})'.format(self.__natural)
        subreps = []
        for ent in self.__natural:
            subreps.append(ent.__repr__())
        return 'N<{}>'.format(', '.join(subreps))
    
    def __str__(self):
        if not self.isDefined():
            return 'Undefined'
        if isinstance(self.__natural, int):
            return f'{self.__natural}'
        subreps = []
        for ent in self.__natural:
            subreps.append(ent.__str__())
        return '<{}>'.format(', '.join(subreps))

    def weirdHash(self):
        lst = ''
        if isinstance(self.__natural, int):
            lst += str(self.__natural) + '+'
        if isinstance(self.__natural, list):
            for nat in self.__natural:
                lst += nat.weirdHash() + '+'
        hashlib.md5(lst.encode()).hexdigest()


class NaturalList:
    def __init__(self, content: List[Natural]=[]):
        self.content = content.copy()
    
    def __add__(self, other: 'NaturalList'):
        return NaturalList(self.content.copy() + other.content.copy())

    def __getitem__(self, index: int):
        if index >= len(self.content):
            return Natural(None)
        return self.content[index]

    def __setitem__(self, index: int, value: Natural):
        while len(self.content) <= index:
            self.content.append(Natural(0))
        self.content[index] = value

    def __len__(self):
        return len(content)
    
    def drop(self, nitem: int):
        if len(self.content) < nitem:
            return NaturalList([])
        return NaturalList(self.content.copy()[nitem:])
