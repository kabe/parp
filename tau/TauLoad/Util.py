#!/usr/bin/env python

"""Utility functions."""

import sys
import re


def sharp_div(line):
    """Divide a line with second sharp ("#").

    @param line line to devide with "#"

    >>> sharp_div("# hoge fuga piyo # <metadata> # foo </metadata>")
    ('hoge fuga piyo', '<metadata> # foo </metadata>')
    >>> sharp_div("# hoge fuga piyo<metadata> # foo </metadata>")
    ('hoge fuga piyo', '<metadata> # foo </metadata>')
    """
    #print line
    r = re.compile(r"# (?P<column>[\w\s]+)( # )?" + \
                       r"(?P<xml><metadata>.+</metadata>$)")
    m = r.match(line)
    return m.group("column"), m.group("xml")


def repl_func(tmpl, funcmap):
    """Replace addr=<0x...> expression with func().

    @param tmpl
    @param funcmap

    >>> import nm.loader
    >>> maploader = nm.loader.Loader("testcase/solver_mpi_tau_pdt.map")
    >>> maploader.load_all()
    >>> repl_func("addr=<0x425d1b> => addr=<0x41e81b>",
    ...           maploader)
    'daxpy2() => time_lap()'
    >>> repl_func("addr=<0x41e610>",
    ...           maploader)
    'my_malloc()'
    >>> repl_func("addr=<0x426359> => MPI_Allreduce()",
    ...           maploader)
    'dot() => MPI_Allreduce()'
    >>> repl_func("MPI_Reduce()",
    ...           maploader)
    'MPI_Reduce()'
    """
    def addr2funcname(funcmap, match):
        """Replace addr to function name.

        @param funcmap FunctionMap
        @param match MatchObject
        """
        hexaddr_s = match.group("hexaddr")
        addr_s = str(int(hexaddr_s, 16))
        try:
            funcname = funcmap.func_ptr_table[addr_s]
        except KeyError, e:
            sys.stderr.write("KeyError: addr=%s\n" % (hexaddr_s))
            raise
        return funcname + "()"

    r = re.compile(r"addr=<0x(?P<hexaddr>[0-9A-Fa-f]+)>")
    s = r.sub(lambda x: addr2funcname(funcmap, x), tmpl)
    return s

if __name__ == '__main__':
    import doctest
    doctest.testmod()
