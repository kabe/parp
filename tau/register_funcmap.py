#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Insert all records into the database
#

import sys
import os
import os.path

import pg

from TauLoad.Loader import Loader
import nm.loader


def main(argv):
    """Main

    Arguments:
    - `argv`:
    """
    if len(argv) < 3:
        sys.stderr.write("Usage: %s APPNAME FUNCMAPFILE" % (argv[0]))
        sys.exit(1)
    # Data Prepare
    app_name = argv[1]
    funcmapfile = argv[2]
    funcmap = nm.loader.Loader(funcmapfile)
    funcmap.load_all()
    # DB prepare
    conn = pg.connect("kabe", "127.0.0.1")
    # Register Funcmap

    conn.inserttable("funcmap",
                     [(funcname, addr, app_name)
                      for funcname, addr in funcmap.func_a_table.iteritems()])
    conn.close()

if __name__ == '__main__':
    main(sys.argv)
