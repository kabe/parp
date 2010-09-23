#!/usr/bin/env python2.6

import sys

import gprof2dot.gprof2dot


def descendants(parser, f):
    """list all descendants of f.

    Parameters:
    - parser: gprof2dot's parser
    - f: function
    """
    if not f.children:
        return []
    retlist = []
    #q = [parser.functions[g.index] for g in f.children]
    q = [f]
    #retlist.extend([f for f in q if not f.cycle])
    while q:
        g = q.pop()
        cs = [parser.functions[h.index] for h in g.children
                        if not parser.functions[h.index] in retlist]
        retlist.extend(cs)
        q.extend(cs)
    return retlist


def select_funcs(parser):
    """Select Functions to output as self time and cumulative time.

    Arguments:
    - `parser`:
    """
    s = []  # self functions
    c = []  # cumulative functions
    r = []  # removed for cumulation functions
    # divide functions into s and c
    for k, v in parser.functions.iteritems():
        if v.name == "main":  # time of main unnecessary
            continue
        try:
            if v.name.startswith("PMPI") \
                    or v.name.index("MPI_Init") >= 0:
                c.append(v)
            else:
                s.append(v)
        except ValueError:
            s.append(v)
    # Remove functions who is a descendant of any function in c
    for cf in c:
        for df in descendants(parser, cf):
            r = [s.pop(i) for i, sf in enumerate(s) if sf.name == df.name]
    return s, c, r


def main():
    """
    """
    fp = sys.stdin
    if len(sys.argv) > 1:
        fp = open(sys.argv[1])
    parser = gprof2dot.gprof2dot.GprofParser(fp)
    parser.parse()
    selffuncs, cumfuncs, removedfuncs = select_funcs(parser)
    print [f.name for f in selffuncs]

if __name__ == '__main__':
    main()
