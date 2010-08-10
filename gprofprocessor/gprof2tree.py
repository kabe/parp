#!/usr/bin/env python2.6

import sys

import gprof2dot.gprof2dot

def main() :
    """
    """
    fp = sys.stdin
    if len(sys.argv) > 1:
        fp = open(sys.argv[1])
    parser = gprof2dot.gprof2dot.GprofParser(fp)
    parser.parse()


if __name__ == '__main__' :
    main()
