#!/usr/bin/env python

#
# tableutil.py
#

def remove_unnecessary_funcs(r_main, appviewname, yaml):
    """Remove unnecessary functions from r_main using yaml

    @param r_main main columns result from the database
    @param appviewname application view name
    @param yaml YAML object including which functions to show
"""
    r_new = []
    appdic = yaml[appviewname]
    funcnames = [f for f in appdic if appdic[f][1] == 1]
    print "Funcnames: %s" % (funcnames)
    for f in r_main:
        if f[0] in funcnames:
            r_new.append(f)
    return tuple(r_new)
