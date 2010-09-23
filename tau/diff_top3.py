#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Calcurates difference of max and min of exclusive function execution time and
# Prints the function's profile
#

import sys
import os
import os.path
import dircache

from TauLoad.Loader import Loader
import nm.loader


def main(argv):
    """Main

    Arguments:
    - `argv`:
    """
    if len(argv) < 2:
        sys.stderr.write("Usage: %s LOGDIR FUNCMAPFILE" % (argv[0]))
        sys.exit(1)
    logdir = argv[1]
    funcmapfile = argv[2]
    dir_contents = dircache.listdir(logdir)
    funcmap = nm.loader.Loader(funcmapfile)
    funcmap.load_all()
    profs = [Loader(os.path.join(logdir, f), funcmap)
             for f in dir_contents if f.startswith("profile")]
    [loader.load_all() for loader in profs]
    maxmintable = dict()
    #print profs[0].profile
    # あるプロファイルには存在する関数が
    # 他のプロファイルには存在しない場合も十分にある
    # SPMDとは限らないので注意が必要。
    # 多分モジュール化が必要
    for funcname, func in profs[0].profile.function.iteritems():
        #print "Processing %s ..." % (funcname)
        max_time = 0
        min_time = 0xFFFFFFFFFFFFFFFF
        for loader in profs:
            try:
                excl_time = loader.profile.function[funcname].attr["excl"]
                calls = loader.profile.function[funcname].attr["calls"]
                f_time = excl_time / calls
            except KeyError, e:
                pass
                #print loader.filename
                #print e
                #raise
            else:
                max_time = max(max_time, f_time)
                min_time = min(min_time, f_time)
        maxmintable[funcname] = (max_time, min_time)
    #print maxmintable
    ranking = sorted(maxmintable,
                     cmp=lambda x, y:
                         cmp((maxmintable[x][0] - maxmintable[x][1]),
                             (maxmintable[y][0] - maxmintable[y][1])),
                     reverse=True)
    print "# FUNCTION MAX-MIN[us] MAX[us] MIN[us]"
    for f in ranking:
        if f.find("=>") == -1:
            print "%s,%.1f,%.1f,%.1f" % \
                (f, maxmintable[f][0] - maxmintable[f][1],
                 maxmintable[f][0], maxmintable[f][1])


if __name__ == '__main__':
    main(sys.argv)
