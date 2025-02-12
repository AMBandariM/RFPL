import sys
sys.setrecursionlimit(1000000)

from rfpl.natural import Natural, NaturalList
from rfpl.rfpy import RFPYModule, define

class Basics(RFPYModule):
    @define(narg=2)
    def Add(self, args):
        return args[1] + args[0]

    @define(narg=2)
    def Sub(self, args):
        return args[1] - args[0]

    @define(narg=2)
    def Mul(self, args):
        return args[1] * args[0]

    @define(narg=2)
    def Pow(self, args):
        return args[1] ** args[0]

    @define(narg=2)
    def Get(self, args):
        if not args[1].is_defined():
            return Natural(None)
        if args[1].is_zero():
            return Natural(0)
        return args[1].get_entry(args[0])

    @define(narg=3)
    def Set(self, args):
        if not args[2].is_defined():
            return Natural(None)
        if args[2].is_zero():
            return Natural(0)
        return args[2].set_entry(args[0], args[1])

    @define(narg=1)
    def Int(self, args):
        if not args[0].is_defined():
            return Natural(None)
        result = args[0].copy()
        result.simplify()
        return result

    @define(narg=1)
    def List(self, args):
        if not args[0].is_defined():
            return Natural(None)
        result = args[0].copy()
        if not result.is_zero():
            result.factor()
        return result

    @define(narg=2)
    def Mod(self, args):
        return args[0] % args[1]
    
    @define(narg=1)
    def IsZero(self, args):
        if not args[0].is_defined():
            return Natural(None)
        if args[0].is_zero():
            return Natural(1)
        return Natural(0)
    
    @define(narg=1)
    def IsOne(self, args):
        if not args[0].is_defined():
            return Natural(None)
        if args[0].is_one():
            return Natural(1)
        return Natural(0)
    
    @define(narg=2)
    def Equal(self, args):
        if not args[0].is_defined() or not args[1].is_defined():
            return Natural(None)
        if args[0] == args[1]:
            return Natural(1)
        return Natural(0)

    @define(narg=1, nbase=2)
    def Prz(self, blist, args):
        # EXPERIMENTAL
        # to be discussed later: basically every function can be modeled as an infinite list:
        # f(0, xs..), f(1, xs..), f(2, xs..), ... a list for every xs
        # Pr is the strict left fold function, starting from f(0, ..).
        # This function (Prz) is the lazy right fold equivalent of Pr.
        # If we allowed recursive definitions, this function could be written in rfpl.
        n = args[0]
        args = args.drop(1)
        if n.is_zero():
            return self.call_base(blist, 0, args)
        n = Natural(int(n) - 1)
        args = NaturalList([
            Natural(lambda args=args : self.Prz(blist, NaturalList([n]) + args)),
            n
        ]) + args
        return self.call_base(blist, 1, args)        
