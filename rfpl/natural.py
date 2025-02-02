from typing import Union, List, Callable
import hashlib
from .RFPLParser import RFPLParser

primes = [2, 3, 5, 7]

def get_prime(i):
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

    def __init__(self, natural: Union[int, List['Natural'], Callable[[], 'Natural']]):
        if isinstance(natural, int) and natural < 0:
            raise Exception(f'Cannot initialize natural with negative number {natural}')
        self.__natural = natural

    def normalize(self):
        while callable(self.__natural):
            self.__natural = self.__natural().__natural
    
    def is_defined(self):
        self.normalize()
        return self.__natural is not None

    def is_zero(self):
        self.normalize()
        return self.__natural == 0
    
    def is_one(self):
        self.normalize()
        if isinstance(self.__natural, int):
            return self.__natural == 1
        return self.is_defined() and all(x.is_zero() for x in self.__natural)
    
    def __int__(self):
        if not self.is_defined():
            return -1
        if isinstance(self.__natural, int):
            return self.__natural
        num = 1
        for i, ent in enumerate(self.__natural):
            num *= get_prime(i) ** int(ent)
        return num
    
    def simplify(self):
        self.__natural = int(self)

    def factor(self):
        if isinstance(self.__natural, list):
            return
        if self.is_zero() or not self.is_defined():
            raise Exception('Zero or undefined cannot be factored')
        cur = self.__natural
        self.__natural = []
        pi = 0
        while cur > 1:
            cnt = 0
            while cur % get_prime(pi) == 0:
                cur //= get_prime(pi)
                cnt += 1
            self.__natural.append(Natural(cnt))
            pi += 1
    
    def copy(self):
        if not self.is_defined():
            return Natural(None)
        if isinstance(self.__natural, int):
            return Natural(self.__natural)
        natural = []
        for nat in self.__natural:
            natural.append(nat.copy())
        return Natural(natural)
    
    def trim(self):
        if not self.is_defined():
            return
        if not isinstance(self.__natural, list):
            return
        while len(self.__natural) > 0 and self.__natural[-1].is_zero():
            self.__natural.pop()

    def get_entry(self, ind: 'Natural'):
        if not self.is_defined() or not ind.is_defined():
            return Natural(None)
        ind = int(ind)
        self.factor()
        if ind >= len(self.__natural):
            return Natural(0)
        return self.__natural[ind]
        
    def set_entry(self, ind: 'Natural', nat: 'Natural'):
        if not self.is_defined() or not ind.is_defined():
            return Natural(None)
        self.factor()
        result = self.copy()
        ind = int(ind)
        while len(result.__natural) <= ind:
            result.__natural.append(Natural(0))
        result.__natural[ind] = nat
        result.trim()
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
        if not self.is_defined():
            return Natural(None)
        return Natural(int(self) + 1)
    
    def __add__(self, other: 'Natural'):
        if not self.is_defined() or not other.is_defined():
            return Natural(None)
        return Natural(int(self) + int(other))

    def __sub__(self, other: 'Natural'):
        if not self.is_defined() or not other.is_defined():
            return Natural(None)
        return Natural(max(int(self) - int(other), 0))
    
    def __mul__(self, other: 'Natural'):
        if not self.is_defined() or not other.is_defined():
            return Natural(None)
        if isinstance(self.__natural, int) or isinstance(other.__natural, int):
            return Natural(int(self) * int(other))
        a = self.__natural.copy()
        b = other.__natural.copy()
        if len(b) < len(a):
            a, b = b, a
        for i in range(len(a)):
            b[i] = b[i] + a[i]
        return Natural(b)

    def __pow__(self, other: 'Natural'):
        if not self.is_defined() or not other.is_defined():
            return Natural(None)
        if other.is_zero():
            return Natural(1)
        if other.is_one():
            return Natural(self.__natural)
        if isinstance(self.__natural, int):
            p = int(other)
            return Natural(self.__natural ** p)
        return Natural(list(x * other for x in self.__natural))

    def __mod__(self, other: 'Natural'):
        if not self.is_defined() or not other.is_defined():
            return Natural(None)
        if other.is_zero():
            return self
        return Natural(int(self) % int(other))
    
    def __eq__(self, other: 'Natural'):
        if not self.is_defined() or not other.is_defined():
            # two undefineds are not equal
            return False
        if isinstance(self.__natural, list) and isinstance(other.__natural, list):
            self.trim()
            other.trim()
            return self.__natural == other.__natural
        return int(self) == int(other)
    
    def __repr__(self):
        if not self.is_defined():
            return 'Undefined'
        if isinstance(self.__natural, int):
            return 'N({})'.format(self.__natural)
        subreps = []
        for ent in self.__natural:
            subreps.append(ent.__repr__())
        return 'N<{}>'.format(', '.join(subreps))
    
    def __str__(self):
        if not self.is_defined():
            return 'Undefined'
        if isinstance(self.__natural, int):
            return f'{self.__natural}'
        subreps = []
        for ent in self.__natural:
            subreps.append(ent.__str__())
        return '<{}>'.format(', '.join(subreps))

    def weird_hash(self):
        # TODO: needs to be changed
        return hashlib.md5(str(self).encode()).hexdigest()


class NaturalList:
    def __init__(self, content: List[Natural]=None):
        self.content = content or []

    def copy(self):
        return NaturalList(self.content.copy())
    
    def __add__(self, other: 'NaturalList'):
        return NaturalList(self.content + other.content)

    def __getitem__(self, index: int):
        if index >= len(self.content):
            return Natural(None)
        return self.content[index]

    def __setitem__(self, index: int, value: Natural):
        while len(self.content) <= index:
            self.content.append(Natural(0))
        self.content[index] = value

    def __len__(self):
        return len(self.content)
    
    def drop(self, nitem: int):
        if len(self.content) < nitem:
            return NaturalList([])
        return NaturalList(self.content.copy()[nitem:])
