import sys
from typing import Callable, TypeVar, Generic, Literal
import collections
import requests

A = TypeVar("A")
B = TypeVar("B")

def profile(f: Callable[A, B], *args: A):
    # a log of f's execution
    trajectory = []

    sys.settrace(makeTrace(trajectory))
    result = f(*args)
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

# functions to be profiled

def fib(x: int) -> int:
    if x < 2:
        return 1
    return fib(x - 1) + fib(x - 2)

def wikiCommonWords():
    import json
    from urllib.request import urlopen

    import collections
    import operator
    import sys

    WIKIPEDIA_ARTICLE_API_URL = "https://en.wikipedia.org/w/api.php?action=query&titles=Spoon&prop=revisions&rvprop=content&format=json"

    def download():
        return urlopen(WIKIPEDIA_ARTICLE_API_URL).read()

    def parse(json_data):
        return json.loads(json_data)

    def most_common_words(page):
        word_occurences = collections.defaultdict(int)

        for revision in page["revisions"]:
            article = revision["*"]

            for word in article.split():
                if len(word) < 2:
                    continue
                word_occurences[word] += 1

        word_list = sorted(word_occurences.items(), key=operator.itemgetter(1), reverse=True)

        return word_list[0:5]

    data = parse(download())
    page = list(data["query"]["pages"].values())[0]

    sys.stderr.write("The most common words were %s\n" % most_common_words(page))



if __name__ == "__main__":
    result = profile(lambda _: fib(7), None)
    print(uploadSummary(summariseTrajectory(result[1])))
