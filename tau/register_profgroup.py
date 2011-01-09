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
import tau

from TauLoad.Loader import Loader
import nm.loader
import util


## Version information
version = "1.0"


def insert_profile(options, profs, exec_id, conn):
    """Insert profiles.

    @param options command-line options
    @param profs
    @param exec_id
    @param conn
    """
    for loader in profs:
    # Insert profile info
        rank = util.filename2rank(loader.filename)
        for funcname, func in loader.profile.function.iteritems():
            pdic = dict()
            pdic["rank"] = rank
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
    """Load profile logs files under the specified directory.

    @param logdir directory name for profile logs
    @param funcmapfile name of function-address mapping file
    @return profiles list
    """
    dir_contents = os.listdir(logdir)
    funcmap = nm.loader.Loader(funcmapfile)
    funcmap.load_all()
    profs = [Loader(os.path.join(logdir, f), funcmap)
             for f in dir_contents if f.startswith("profile")]
    [loader.load_all() for loader in profs]
    return profs


def node_set(profs):
    """Set of nodes in the profile logs.

    Node name is in the metadata XML like the following line.
    @verbatim
    <attribute><name>Node Name</name><value>foonode</value></attribute>
    @endverbatim

    @param profs profile log data
    @return set of node names
    """
    nodes = [attr.find("value").string
             for loader in profs
             for attr in loader.soup.findAll("attribute")
             if attr.find("name").string == "Node Name"]
    return set(nodes)


def prepare_registration(options, profs):
    """Prepare data for the profile log registration to the database.

    @param options command-line options (OptionParser)
    @param profs profile log data
    @return dictionary including all information
    """
    d = dict()
    d["profs"] = profs
    d["node_set"] = node_set(profs)
    d["nodes"] = len(d["node_set"])
    d["nproc"] = len(profs)
    # XML metadata dictionary from main profile log
    lcands = [p for p in profs if p.filename.endswith("profile.0.0.0")]
    assert(len(lcands) == 1)
    d["main_loader"] = lcands[0]
    d["soupdic"] = util.soup2dic(d["main_loader"].soup)
    # Place of execution
    d["place"] = util.getplacename(options, d)
    # Execution time
    d["start_ts"] = int(d["soupdic"]["Starting Timestamp"])
    t0 = int(d["soupdic"]["Starting Timestamp"])
    t1 = int(d["soupdic"]["Timestamp"])
    d["exec_time"] = (t1 - t0) / 1e6
    if options.verbose >= 3:
        util.out("Infodic: ", d)
    return d


def add_profgroup(options, conn, info_dic):
    """Prepares to add a profgroup.

    Gets some information needed to insert a new profgroup record.
    @param options command-line options
    @param conn connection object to the database
    @param info_dic information to add
    @return group id to insert
    """
    try:
        group_id = _add_profgroup(options, conn, info_dic)
    except KeyError, e:
        util.err("KeyError Occurred in adding a profile group!")
        raise e
    return group_id


def _add_profgroup(options, conn, pd):
    """Safely insert profgroup.
    If a record with the same profgroup condition exists,
    it only returns the id column of that,
    otherwise it inserts a new record and returns the id.

    @param options command-line options
    @param conn database connection object
    @param pd dictionary containing all profile information
    @return id of profgroup to insert into profexec table
    """
    sql_s = """SELECT id
               FROM profgroup
               WHERE
                   application = ?
               AND nodes = ?
               AND procs = ?
               AND place = ?;
               """
    rtup = conn.select(sql_s,
                       (pd["soupdic"]["Executable"].encode('utf_8'),
                        pd["nodes"],
                        pd["nproc"],
                        pd["place"].encode('utf_8')))
    if len(rtup) == 0:
        if options.verbose >= 1:
            util.out("No such profgroup. will newly insert...")
        pginsert = {
            "application": pd["soupdic"]["Executable"].encode('utf_8'),
            "nodes": pd["nodes"],
            "procs": pd["nproc"],
            "place": pd["place"].encode('utf_8')}
        if options.verbose >= 3:
            util.out("new profgroup dict", pginsert)
        rdic = conn.insert("profgroup", pginsert)
        rt = rdic["id"]
        if options.verbose >= 1:
            util.out("New profgroup %d: %s" % (rt, pginsert))
    else:
        if options.verbose >= 1:
            util.out("Using existing profgroup ...")
        rt = rtup[0][0]
    return rt


def add_profexec(options, conn, group_id, infodic):
    """Insert a record of profexec table.

    @param options command-line options
    @param conn database connection
    @param group_id id of profgroup table
    @param infodic dictionary of all information
    @return the id of profexec table
    """
    exec_time = infodic["exec_time"]
    start_ts = infodic["start_ts"]
    i_dic = {
        "profgroup_id": group_id,
        "exec_time": exec_time,
        "start_ts": start_ts}
    sql_s = """SELECT id FROM profexec
               WHERE profgroup_id = ?
                 AND start_ts = ?;"""
    # large integer has suffix "L", which should be removed by str()
    rtup = conn.select(sql_s, (group_id, str(start_ts)))
    if len(rtup) == 0:
        if options.verbose >= 1:
            util.out("No such profexec. will newly insert...")
        rdic = conn.insert("profexec", i_dic)
        exec_id = rdic["id"]
        if options.verbose >= 2:
            util.out("new exec id", exec_id)
        return exec_id
    else:
        raise Exception("Same Profexec exists, aborting")


def parse_opt():
    """Parse Command Line Arguments.

    @todo これを実際に使うようにする
    """
    from optparse import OptionParser
    usage = "Usage: %prog [options] LOGDIR FUNCMAPFILE"
    parser = OptionParser(usage=usage, version="%prog " + version)
    parser.add_option("-v", "--verbose", dest="verbose",
                      action="count", default=0,
                      help="verbose output (more -v shows more output)")
    parser.add_option("-b", "--abort", dest="finally_abort",
                      action="store_true", default=False,
                      help="finally abort (thus no side-effect)")
    parser.add_option("-p", "--place", dest="place",
                      help="specify execution place as PLACE",
                      metavar="PLACE")
    parser.add_option("-l", "--library", dest="library",
                      help="specify library used as LIBRARY",
                      metavar="LIBRARY")
    (options, args) = parser.parse_args()
    if len(args) != 2:
        parser.error("incorrect number of arguments: run with -h")
    return options, args


def main():
    """Main function.

    @todo library などの指定を可能にする
    @todo SQLite3 のとき DB ファイルの指定を可能にする
    @todo -t でテストにする
    @todo class Parp など
    """
    options, args = parse_opt()
    # Data Prepare
    logdir = args[0]
    funcmapfile = args[1]
    profs = load_profs(logdir, funcmapfile)
    # Unique nodes list
    nodeset = node_set(profs)
    # Prepare information to add
    d = prepare_registration(options, profs)
    # DB prepare
    #conn = db.init("postgres", username="kabe", hostname="127.0.0.1")
    conn = db.init("sqlite3", dbfile="/home/kabe/Archives/prof.db")
    ### BEGIN TRANSACTION ###
    conn.begin_transaction()
    # Register
    try:
        # Profgroup
        group_id = add_profgroup(options, conn, d)
        # ProfExec Insert
        profexec_id = add_profexec(options, conn, group_id, d)
        util.out(group_id, profexec_id)
        # Profile Insert
        insert_profile(options, profs, profexec_id, conn)
    except Exception, e:
        util.err("Exception in main", repr(e))
        conn.rollback_transaction()
        raise e  # Re-raise the exception
    # Finalization
    if options.finally_abort:
        conn.rollback_transaction()
        conn.close()
        if options.verbose >= 1:
            util.out("Commit normally aborted")
    else:
        ### COMMIT TRANSACTION ###
        conn.commit_transaction()
        conn.close()
        if options.verbose >= 1:
            util.out("Commit OK")

if __name__ == '__main__':
    #tau.run('main(sys.argv)')
    main()
