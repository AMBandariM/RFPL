# my temporary answer to circular imports!

from dataclasses import dataclass, field
from typing import List, Dict, Callable

from .natural import Natural, NaturalList
from .RFPLParser import RFPLParser

@dataclass
class BaseList:
    args: List[RFPLParser.FexprContext]
    prev: 'BaseList' = None


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


@dataclass
class SymbolEntry:
    symbol: str
    call: Callable[[BaseList, NaturalList], Natural]
    builtin: bool = False
    ix: int = -1
    ftype: FunctionType = field(default_factory=FunctionType)

