from dataclasses import dataclass
from typing import Callable, List

from .natural import NaturalList
from .symbol import BaseList, FunctionType, SymbolEntry


@dataclass
class ExportInfo:
    name: str
    narg: int
    nbase: int = 0


class RFPYModule:
    def __init__(self, interpreter):
        # I really love to add type info for interpreter, without introducing circular imports
        self.interpreter = interpreter

    def export_symbols(self) -> List[SymbolEntry]:
        symbols = []
        for name in dir(self):
            func = getattr(self, name)
            if callable(func) and hasattr(func, 'c_export'):
                exp: ExportInfo = func.c_export
                call = func
                if exp.nbase == 0:
                    call = lambda _blist, args, func=func : func(args)
                symbols.append(SymbolEntry(
                    symbol=exp.name,
                    call=call,
                    ftype=FunctionType(narg=exp.narg, nbase=exp.nbase)
                ))
        return symbols
    
    def call_base(self, blist: BaseList, ix: int, args: NaturalList):
        return self.interpreter.interpret_fexpr(blist.args[ix], blist.prev, args)


def define(*, narg, name=None, nbase=0):
    def decorator(func: Callable):
        nonlocal name
        name = name or func.__name__
        func.c_export = ExportInfo(
            name=name,
            narg=narg,
            nbase=nbase,
        )
        return func
    return decorator
