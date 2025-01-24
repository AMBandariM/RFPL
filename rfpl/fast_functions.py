from typing import Callable, Dict
from dataclasses import dataclass, field
import inspect
import ast
from .symbol import BaseList, FunctionType, SymbolEntry

def fast_function(func_registry: Dict[str, SymbolEntry], narg):
    def decorator(func: Callable):
        name = func.__name__
        func_registry[name] = SymbolEntry(
            symbol=name,
            call=func,
            builtin=True,
            ftype=FunctionType(narg=narg),
        )
        return func
    return decorator
