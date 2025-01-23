from typing import Callable, Dict
from dataclasses import dataclass, field
import inspect
import ast
from .symbol import BaseList, FunctionType, SymbolEntry

def fast_function(func_registry: Dict[str, SymbolEntry]):
    def decorator(func: Callable):
        name = func.__name__

        source = inspect.getsource(func)
        tree = ast.parse(source)

        class ArgVisitor(ast.NodeVisitor):
            def __init__(self):
                self.max_index = -1

            def visit_Subscript(self, node):
                if isinstance(node.value, ast.Name) and node.value.id == 'args':
                    if isinstance(node.slice, ast.Index):  # Python < 3.9
                        index_node = node.slice.value
                    elif isinstance(node.slice, ast.Constant):  # Python 3.9+
                        index_node = node.slice
                    else:
                        return
                    if isinstance(index_node, ast.Constant) and isinstance(index_node.value, int):
                        self.max_index = max(self.max_index, index_node.value)

        visitor = ArgVisitor()
        visitor.visit(tree)

        narg = visitor.max_index + 1 if visitor.max_index >= 0 else 0

        func_registry[name] = SymbolEntry(
            symbol=name,
            call=func,
            builtin=True,
            ftype=FunctionType(narg=narg),
        )
        return func

    return decorator