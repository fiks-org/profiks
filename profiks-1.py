import sys
from typing import Callable, TypeVar, Generic

A = TypeVar("A")
B = TypeVar("B")

def profile(f: Callable[A, B], args: A) -> B:
    sys.settrace(trace)
    result = f(args)
    sys.settrace(emptyTrace)
    return result

def emptyTrace(_, __, ___):
    return None

def trace(frame, event, arg):
    pass

def fib(x: int) -> int:
    if x < 2:
        return 1
    return fib(x - 1) + fib(x - 2)

if __name__ == "__main__":
    for i in range(0, 7):
        print(profile(fib, i))
