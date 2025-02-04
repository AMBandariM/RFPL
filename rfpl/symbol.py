# my temporary answer to circular imports!

from dataclasses import dataclass, field
from typing import List, Dict, Callable
from .RFPLParser import RFPLParser
from .natural import Natural, NaturalList

@dataclass
class BaseList:
    args: List[RFPLParser.FexprContext]
    prev: 'BaseList' = None

    def __eq__(self, other):
        if not isinstance(other, BaseList):
            return False
        if len(self.args) != len(other.args):
            return False
        if any(a.c_ix != b.c_ix for a, b in zip(self.args, other.args)):
            return False
        return self.prev == other.prev

    def __hash__(self):
        ixs = tuple(a.c_ix for a in self.args)
        return hash((ixs, self.prev))

@dataclass
class FunctionType:
    narg: int = 0
    nbase: int = 0
    max_narg_b: Dict = field(default_factory=dict)
    relative_narg_b: Dict = field(default_factory=dict)

    # narg is the minimum number of argument this function needs, without considering bases.
    # nbase is the number of base arguments (@0, @1, ...) this function uses.
    # @i.narg <= max_narg_b[i]
    # narg >= @i.narg + relative_narg_b[i]
    # The dictionaries may not have a value for i, indicating @i is not mentioned in the function.
    # Every fexpr has a type.

    instant: bool = True


@dataclass
class SymbolEntry:
    symbol: str
    call: Callable[[BaseList, NaturalList], Natural]
    builtin: bool = False
    ix: int = -1
    ftype: FunctionType = field(default_factory=FunctionType)

