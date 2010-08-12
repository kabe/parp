#!/usr/bin/env python2.6

import sys

import gprof2dot.gprof2dot

def descendants(parser, f):
    if not f.children: return []
    print "Traversing %s" % (f.name)
    li = [parser.functions[g.index] for g in f.children]
    for fx in f.children:
        if fx.cycle: continue
        fobj = parser.functions[fx.index]
        li.extend([g for g in descendants(parser, fobj)])
    return li

def select_funcs(parser) :
    """Select Functions to output as self time and cumulative time.
    
    Arguments:
    - `parser`:
    """
    s = []
    c = []
    # divide functions into s and c
    for k, v in parser.functions.iteritems():
        if v.name.startswith("PMPI"):
            c.append(v)
        else :
            s.append(v)
    # Remove functions who has an ancestor has the name starts with "PMPI"
    #for f in c:
    print [f.index for f in s if f.name == "daxpy"]
    #print (f.name for f in descendants(parser, s[0]))
    print descendants(parser, parser.functions[241])
    return s, c

def main() :
    """
    """
    fp = sys.stdin
    if len(sys.argv) > 1:
        fp = open(sys.argv[1])
    parser = gprof2dot.gprof2dot.GprofParser(fp)
    parser.parse()
    selffuncs, cumfuncs = select_funcs(parser)

if __name__ == '__main__' :
    main()
