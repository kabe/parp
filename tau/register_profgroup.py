#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Insert all records into the database
#

import sys
import os
import os.path
import re

import pg

from TauLoad.Loader import Loader
import nm.loader


def hostname2clustername(hostname):
    """Convert hostname to cluster name.

    Arguments:
    - `hostname`: hostname in string
    >>> hostname2clustername("hongo100")
    'hongo'
    >>> hostname2clustername("hongo")
    'hongo'
    """
    r = re.compile(r"^([a-zA-Z]+)(\d+)?$")
    m = r.match(hostname)
    return m.groups()[0]


def filename2rank(filename):
    """Pick up the rank of the process.

    Arguments:
    - `filename`:
    """
    #print filename
    r = re.compile(r".*profile\.(\d+)\.(\d+).(\d+)$")
    m = r.match(filename)
    return m.group(1)


def main(argv):
    """Main

    Arguments:
    - `argv`:
    """
    if len(argv) < 2:
        sys.stderr.write("Usage: %s LOGDIR FUNCMAPFILE" % (argv[0]))
        sys.exit(1)
    # Data Prepare
    logdir = argv[1]
    funcmapfile = argv[2]
    dir_contents = os.listdir(logdir)
    funcmap = nm.loader.Loader(funcmapfile)
    funcmap.load_all()
    profs = [Loader(os.path.join(logdir, f), funcmap)
             for f in dir_contents if f.startswith("profile")]
    [loader.load_all() for loader in profs]
    # Unique nodes list
    nodes = [attr.find("value").string
             for loader in profs
             for attr in loader.soup.findAll("attribute")
             if attr.find("name").string == "Node Name"]
    nodeset = set(nodes)
    # DB prepare
    #conn = pg.connect("kabe", "127.0.0.1")
    db = pg.DB("kabe", "127.0.0.1")
    # Register
    # Profgroup
    profgroup_dic = dict()
    profgroup_dic["procs"] = len(profs)
    #loader = profs[0]
    lcands = filter(lambda prof: prof.filename.endswith("profile.0.0.0"), profs)
    assert(len(lcands) == 1)
    loader = lcands[0]
    # print loader.filename
    #print loader.soup
    for attr in loader.soup.findAll("attribute"):
        #print [attr.find("name").string, attr.find("value").string]
        if attr.find("name").string == "Executable":
            appname = attr.find("value").string
            profgroup_dic["application"] = db.escape_string(appname)
        if attr.find("name").string == "Hostname":
            cl_name = hostname2clustername(attr.find("value").string)
            profgroup_dic["place"] = db.escape_string(cl_name)
        #if attr.find("name").string == "Hostname":
    profgroup_dic["nodes"] = len(nodeset)
    print "Insert %s" % (str(profgroup_dic))
    rdic = db.insert("profgroup", profgroup_dic)
    print rdic
    group_id = rdic["id"]
    print "ID=%d" % (rdic["id"])
    # Profile
    #group_id = 100
    for loader in profs:
        # Insert profile info
        rank = filename2rank(loader.filename)
        for funcname, func in loader.profile.function.iteritems():
            pdic = dict()
            pdic["rank"] = rank
            #print "Processing %s ..." % (funcname)
            pdic["funcname"] = funcname
            pdic["profgroup_id"] = group_id
            try:
                pdic["incl"] = func.attr["incl"]
                pdic["excl"] = func.attr["excl"]
                pdic["subrs"] = func.attr["subrs"]
                pdic["calls"] = func.attr["calls"]
                pdic["group_s"] = func.attr["group"]
            except KeyError, e:
                raise
            try:
                rdic = db.insert("profile", pdic)
                #print rdic
            finally:
                pass
        # Insert userevent info (not implemented yet)
        #print loader.userevents.columns
        #for eventname, event in loader.userevents.iteritems():
        #    print (eventname, event)
    # Finalization
    db.close()

if __name__ == '__main__':
    main(sys.argv)
