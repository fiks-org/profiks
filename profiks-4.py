import sys
from typing import Callable, TypeVar, Generic, Literal
import collections
import requests

A = TypeVar("A")
B = TypeVar("B")

def profile(f: Callable[A, B], args: A):
    # a log of f's execution
    trajectory = []

    sys.settrace(makeTrace(trajectory))
    result = f(args)
    sys.settrace(emptyTrace)
    return [result, trajectory]

def emptyTrace(_, __, ___):
    return None

def makeTrace(trajectory):
    def go(frame, event: Literal["call", "line", "return", "exception", "opcode"], arg):
        if event != "line":
            return go

        stack = [frame.f_code.co_name]
        while frame.f_back != None:
            frame = frame.f_back
            stack.append(frame.f_code.co_name)

        stack.reverse()
        trajectory.append(stack)
        return go

    return go

def summariseTrajectory(trajectory):
    summary = collections.defaultdict(int)
    for stack in trajectory:
        key = ";".join(stack)
        if key in summary:
            summary[key] += 1
        else:
            summary[key] = 1

    return "\n".join([
        k + " " + str(v) for k, v in summary.items()
    ])

def uploadSummary(summary):
    headers = {'Content-Type': 'application/octet-stream'}
    with requests.post("https://flamegraph.com", data=summary, headers=headers) as resp:
        return resp.text

def fib(x: int) -> int:
    if x < 2:
        return 1
    return fib(x - 1) + fib(x - 2)

if __name__ == "__main__":
    f = lambda x: uploadSummary(summariseTrajectory(profile(fib, x)[1]))

    for i in range(0, 7):
        print(f(i))
