#!/usr/bin/env python

#
# TauLoad.Util
#

import re


def sharp_div(line):
    """Divide a line with second sharp ("#").

    Arguments:
    - `line`:

    >>> sharp_div("# hoge fuga piyo # <metadata> # foo </metadata>")
    ('hoge fuga piyo', '<metadata> # foo </metadata>')
    """
    r = re.compile(r"# (?P<column>[\w\s]+) # (?P<xml>.+$)")
    m = r.match(line)
    return m.group("column"), m.group("xml")


if __name__ == '__main__':
    import doctest
    doctest.testmod()
