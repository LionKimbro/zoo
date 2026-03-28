"""util.py  -- various utilities"""

import time

from symbols import *


## globals

DATA="DATA"
DI="DI"

g = {DATA: None,  # for DATA
     DI: 0}  # for DATA

def incr(k):
    g[k] += 1
    return g[k]-1


## general

def first(L, default=None):
    """Return the first of a list, or default if it has no contents."""
    if L:
        return L[0]
    else:
        return default


## time

def iso8601datelocal():
    return time.strftime("%Y-%m-%d")


## DATA

def data(L):
    g[DATA] = L
    g[DI] = 0

def READ():
    return g[DATA][incr(DI)]

def RESTORE(i=None):
    g[DI] = i or 0

def dmore():
    return g[DI] < len(g[DATA])

def daddr():
    return g[DI]



