#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Insert all records into the database
#

import sys
import os
import os.path
import re

import db

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


def insert_profile(profs, exec_id, conn):
    """Insert profiles.

    Arguments:
    - `profs`:
    - `exec_id`:
    - `conn`:
    """
    for loader in profs:
    # Insert profile info
        rank = filename2rank(loader.filename)
        for funcname, func in loader.profile.function.iteritems():
            pdic = dict()
            pdic["rank"] = rank
            #print "Processing %s ..." % (funcname)
            pdic["funcname"] = funcname
            pdic["profexec_id"] = exec_id
            try:
                pdic["incl"] = func.attr["incl"]
                pdic["excl"] = func.attr["excl"]
                pdic["subrs"] = func.attr["subrs"]
                pdic["calls"] = func.attr["calls"]
                pdic["group_s"] = func.attr["group"]
            except KeyError, e:
                raise
            try:
                rdic = conn.insert("profile", pdic)
            finally:
                pass
        # Insert userevent info (not implemented yet)
        #print loader.userevents.columns
        #for eventname, event in loader.userevents.iteritems():
        #    print (eventname, event)


def load_profs(logdir, funcmapfile):
    dir_contents = os.listdir(logdir)
    funcmap = nm.loader.Loader(funcmapfile)
    funcmap.load_all()
    profs = [Loader(os.path.join(logdir, f), funcmap)
             for f in dir_contents if f.startswith("profile")]
    [loader.load_all() for loader in profs]
    return profs, loader


def add_profexec(conn, group_id, exec_time):
    """Insert a record of profexec table.
    Returns the id of profexec table.

    Arguments:
    - `conn`:
    - `group_id`:
    - `exec_time`:
    """
    i_dic = {"profgroup_id": group_id, "exec_time": exec_time}
    rdic = conn.insert("profexec", i_dic)
    return rdic["id"]


def soup2dic(soup, pg_dic):
    """Select values from soup and register them to pg_dic.

    Arguments:
    - `soup`:
    - `pg_dic`:
    """
    start_time = 0
    end_time = 0
    for attr in soup.findAll("attribute"):
        attrname = attr.find("name").string
        attrvalue = attr.find("value").string
        if attrname == "Executable":
            appname = attrvalue
            pg_dic["application"] = appname
        if attrname == "Hostname":
            cl_name = hostname2clustername(attrvalue)
            pg_dic["place"] = cl_name
        if attrname == "Starting Timestamp":
            start_time = int(attrvalue)
        if attrname == "Timestamp":
            end_time = int(attrvalue)
    pg_dic["exec_time"] = (end_time - start_time) / 1e6
    return pg_dic


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
    profs, loader = load_profs(logdir, funcmapfile)
    # Unique nodes list
    nodes = [attr.find("value").string
             for loader in profs
             for attr in loader.soup.findAll("attribute")
             if attr.find("name").string == "Node Name"]
    nodeset = set(nodes)
    # DB prepare
    conn = db.init("postgres", username="kabe", hostname="127.0.0.1")
    #conn = db.init("sqlite3", dbfile="/home/kabe/Archives/prof.db")
    # Register
    # Profgroup
    profgroup_dic = dict()
    profgroup_dic["procs"] = len(profs)
    lcands = filter(lambda prof: prof.filename.endswith("profile.0.0.0"),
                    profs)
    assert(len(lcands) == 1)
    main_loader = lcands[0]
    soup2dic(main_loader.soup, profgroup_dic)
    profgroup_dic["nodes"] = len(nodeset)
    print "Insert %s" % (str(profgroup_dic))
    rdic = conn.insert("profgroup", profgroup_dic)
    #print rdic
    group_id = rdic["id"]
    #print "ID=%d" % (rdic["id"])
    # ProfExec Insert
    profexec_id = add_profexec(conn, group_id, profgroup_dic["exec_time"])
    print (group_id, profexec_id)
    # Profile
    #group_id = 100
    insert_profile(profs, profexec_id, conn)
    # Finalization
    conn.close()

if __name__ == '__main__':
    main(sys.argv)
