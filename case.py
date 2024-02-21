from collections import namedtuple
from types import ModuleType
from typing import Any, Callable, NamedTuple, Sequence

InOut = namedtuple("InOut", ["input", "output"])

class FuncCall(NamedTuple):
    func: Callable
    args: Sequence
    ans: Any
    output: str

    def callstr(self) -> str:
        return (
            f"{self.func.__name__}"
            f"({', '.join(repr(self.args) for arg in self.args)})"
        )

    def name(self) -> str:
        return f"{self.func.__name__}()"


class RecursiveCall(NamedTuple):
    module: ModuleType
    func: Callable
    args: Sequence
    ans: Any
    output: str
    basecase: bool

    def callstr(self) -> str:
        return (
            f"{self.func.__name__}"
            f"({', '.join(repr(self.args) for arg in self.args)})"
        )
    
    def name(self) -> str:
        return f"{self.func.__name__}()"
    
