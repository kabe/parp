#!/usr/bin/env python


import sys
import os


def strint_maplist(s):
    """Space-separated integer to list of integers.

    @param s Space-separated integer list
    >>> strint_maplist("")
    []
    >>> strint_maplist(" ")
    []
    >>> strint_maplist("  ")
    []
    >>> strint_maplist("145 196 205")
    [145, 196, 205]
    >>> strint_maplist("145")
    [145]
    """
    ss = s.split(" ")
    ints = []
    for t in ss:
        try:
            iv = int(t)
            ints.append(iv)
        except ValueError:
            pass
    return ints


if __name__ == '__main__':
    import doctest
    doctest.testmod()
