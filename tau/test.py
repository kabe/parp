#!/usr/bin/env python

import sys
import os

from TauLoad.Loader import Loader


def main(argv):
    """Main

    Arguments:
    - `argv`:
    """
    if len(argv) < 2:
        sys.stderr.write("Usage: %s LOGFILE" % (argv[0]))
        sys.exit(1)
    loader = Loader(argv[1])
    loader.load_all()

if __name__ == '__main__':
    main(sys.argv)
