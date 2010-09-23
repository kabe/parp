#!/usr/bin/env python

import sys
import os

import nm.loader
from TauLoad.Loader import Loader


def main(argv):
    """Main

    Arguments:
    - `argv`:
    """
    if len(argv) < 2:
        sys.stderr.write("Usage: %s LOGFILE FUNCMAPFILE" % (argv[0]))
        sys.exit(1)
    maploader = nm.loader.Loader(argv[2])
    maploader.load_all()
    loader = Loader(argv[1], maploader)
    loader.load_all()

if __name__ == '__main__':
    main(sys.argv)
