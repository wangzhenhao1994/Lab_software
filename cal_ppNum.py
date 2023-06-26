import numpy
from collections.abc import Iterable

def flatten(l):
    for el in l:
        if isinstance(el, Iterable) and not isinstance(el, (str, bytes)):
            yield from flatten(el)
        else:
            yield el

if __name__ == '__main__':
    pp = 10
    ppNum=list(flatten([['pumponly','probeonly'] if i%(int(pp))==0 and i!=0 else i for i in range(155)]))
    print(numpy.string_(ppNum))
    print(ppNum)
    print(len(ppNum))