from rfpl.natural import Natural
from rfpl.fast_functions import fast_function

basics = {}

@fast_function(basics)
def Add(_blist, args):
    return args[0] + args[1]

@fast_function(basics)
def Sub(_blist, args):
    return args[1] - args[0]