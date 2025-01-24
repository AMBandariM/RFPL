from rfpl.natural import Natural
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
        if args[1].is_zero():
            return Natural(0)
        return args[1].get_entry(args[0])

    @define(narg=3)
    def Set(self, args):
        if args[2].is_zero():
            return Natural(0)
        return args[2].set_entry(args[0], args[1])

    @define(narg=1)
    def Int(self, args):
        result = args[0].copy()
        result.simplify()
        return result

    @define(narg=1)
    def List(self, args):
        result = args[0].copy()
        if result.is_defined() and not result.is_zero():
            result.factor()
        return result

    @define(narg=2)
    def Mod(self, args):
        return args[0] % args[1]
