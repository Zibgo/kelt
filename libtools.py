from typing import Callable

class StackUnpacked(tuple):
    def __new__(cls, *args):
        return super().__new__(cls, args)

    def __init(self, *args):
        pass
    

class Lib:
    def __init__(self, name: str, table: dict[str, Callable[..., Any]]):
        self.name = name
        self._table = table
        self._childs: list[_Lib] = []
    
    def get_table(self) -> dict[Callable[..., Any]]:
        return self._table

    def get_child(self, child_name: str) -> _Lib:
        return next((child for child in self._childs if child.name == child_name), None)

    def add_childs(self, *args: tuple[_Lib]):
        self._childs += args

def nullary(op: Callable) -> Callable:
    return lambda args: op()

def unary(op: Callable) -> Callable:
    return lambda args: op(args[0])

def binary(op: Callable) -> Callable:
    return lambda args: op(args[0], args[1])

def ternary(op: Callable) -> Callable:
    return lambda args: op(args[0], args[1], args[2])

def variadic(op: Callable) -> Callable:
    return lambda args: op(*args)

def collection(op: Callable) -> Callable:
    return lambda args: op(args)
