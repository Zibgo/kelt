import operator
from functools import reduce
from libtools import *

_logical_table = {
    '@and': binary(lambda a, b: a if not a else b),
    '@or': binary(lambda a, b: a if a else b),
    '@not': unary(operator.not_),
    '@truth': unary(operator.truth),
    }

_stack_table = {
    '@dup': unary(lambda a: StackUnpacked(a, a)),
    '@swap': binary(lambda a, b: StackUnpacked(b, a)),
    '@over': binary(lambda a, b: StackUnpacked(a, b, a)),
    }

_io_table = {
    '@read': nullary(input),
    '@print': variadic(lambda *args: print(*args, end=' ')),
    }

_logical = Lib('logical', _logical_table)
_stack = Lib('stack', _stack_table)
_io = Lib('io', _io_table)

_std_table = {
    #arithmetics
    '@add': collection(sum),
    '@sub': binary(operator.sub),
    '@mul': collection(lambda list: reduce(lambda a, b: a * b, list, 1)),
    '@fdiv': binary(operator.floordiv),
    '@tdiv': binary(operator.truediv),
    '@mod': binary(operator.mod),
    '@pow': binary(operator.pow),
    '@neg': unary(operator.neg),
    #comparsions
    '@lt': binary(operator.lt),
    '@gt': binary(operator.gt),
    '@eq': binary(operator.eq),
    '@ne': binary(operator.ne),
    '@le': binary(operator.le),
    '@ge': binary(operator.ge),
    #bitwise
    '@lsh': binary(operator.lshift),
    '@rsh': binary(operator.rshift),
    '@b_and': binary(operator.and_),
    '@b_or': binary(operator.or_),
    '@b_xor': binary(operator.xor),
    '@b_inv': binary(operator.invert),
    }

std = Lib('std', _std_table)
    
std.add_childs(_logical, _stack, _io)
