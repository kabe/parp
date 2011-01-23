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


class Registerer(object):
    """Registerer.
    """

    def __init__(self, ):
        """
        """
        pass

    def insert_profile(self, exec_id):
        """Insert profiles.

        @param self
        @param exec_id profile execution ID
        """
        for loader in self.profs:
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
                    rdic = self.conn.insert("profile", pdic)
                finally:
                    pass
            # Insert userevent info (not implemented yet)
            #print loader.userevents.columns
            #for eventname, event in loader.userevents.iteritems():
            #    print (eventname, event)

    def load_profs(self, logdir, funcmapfile):
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
        ## Profile logs
        self.profs = profs

    def prepare_registration(self):
        """Prepare data for the profile log registration to the database.

        @param self
        """
        d = dict()
        d["profs"] = self.profs
        d["node_set"] = self.nodeset
        d["nodes"] = len(d["node_set"])
        d["nproc"] = len(self.profs)
        # XML metadata dictionary from main profile log
        lcands = [p for p in self.profs
                  if p.filename.endswith("profile.0.0.0")]
        assert(len(lcands) == 1)
        d["main_loader"] = lcands[0]
        d["soupdic"] = util.soup2dic(d["main_loader"].soup)
        # Place of execution
        d["place"] = util.getplacename(self.options, d)
        # Execution time
        d["start_ts"] = int(d["soupdic"]["Starting Timestamp"])
        t0 = int(d["soupdic"]["Starting Timestamp"])
        t1 = int(d["soupdic"]["Timestamp"])
        d["exec_time"] = (t1 - t0) / 1e6
        # library
        d["library"] = util.NVL(self.options.library, "")
        if self.options.verbose >= 3:
            util.out("Infodic: ", d)
        ## Dictionary of all information
        self.infodic = d

    def add_profgroup(self):
        """Prepares to add a profgroup.

        Gets some information needed to insert a new profgroup record.
        @param self
        @return group id to insert
        """
        try:
            group_id = self._add_profgroup()
        except KeyError, e:
            util.err("KeyError Occurred in adding a profile group!")
            raise e
        return group_id

    def _add_profgroup(self):
        """Safely insert profgroup.
        If a record with the same profgroup condition exists,
        it only returns the id column of that,
        otherwise it inserts a new record and returns the id.

        @param self
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
        pd = self.infodic
        rtup = self.conn.select(sql_s,
                                (pd["soupdic"]["Executable"].encode("utf_8"),
                                 pd["nodes"],
                                 pd["nproc"],
                                 pd["place"].encode("utf_8")))
        if len(rtup) == 0:
            if self.options.verbose >= 1:
                util.out("No such profgroup. will newly insert...")
            pginsert = {
                "application": pd["soupdic"]["Executable"].encode("utf_8"),
                "nodes": pd["nodes"],
                "procs": pd["nproc"],
                "place": pd["place"].encode("utf_8"),
                "library": pd["library"].encode("utf_8")}
            if self.options.verbose >= 3:
                util.out("new profgroup dict", pginsert)
            rdic = self.conn.insert("profgroup", pginsert)
            rt = rdic["id"]
            if self.options.verbose >= 1:
                util.out("New profgroup %d: %s" % (rt, pginsert))
        else:
            if self.options.verbose >= 1:
                util.out("Using existing profgroup ...")
            rt = rtup[0][0]
        return rt

    def add_profexec(self, group_id):
        """Insert a record of profexec table.

        @param self
        @param group_id id of profgroup table
        @return the id of profexec table
        """
        exec_time = self.infodic["exec_time"]
        start_ts = self.infodic["start_ts"]
        i_dic = {
            "profgroup_id": group_id,
            "exec_time": exec_time,
            "start_ts": start_ts}
        sql_s = """SELECT id FROM profexec
                   WHERE profgroup_id = ?
                     AND start_ts = ?;"""
        # large integer has suffix "L", which should be removed by str()
        rtup = self.conn.select(sql_s, (group_id, str(start_ts)))
        if len(rtup) == 0:
            if self.options.verbose >= 1:
                util.out("No such profexec. will newly insert...")
            rdic = self.conn.insert("profexec", i_dic)
            exec_id = rdic["id"]
            if self.options.verbose >= 2:
                util.out("new exec id", exec_id)
            return exec_id
        else:
            raise Exception("Same Profexec exists, aborting")

    def parse_opt(self):
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
                          default=None,
                          metavar="PLACE")
        parser.add_option("-l", "--library", dest="library",
                          help="specify library used as LIBRARY",
                          default=None,
                          metavar="LIBRARY")
        (options, args) = parser.parse_args()
        if len(args) != 2:
            parser.error("incorrect number of arguments: run with -h")
        self.options = options
        self.args = args

    def main(self):
        """Main function.

        @param self
        @todo library などの指定を可能にする
        @todo SQLite3 のとき DB ファイルの指定を可能にする
        @todo -t でテストにする
        @todo class Parp など
        """
        self.parse_opt()
        # Data Prepare
        logdir = self.args[0]
        funcmapfile = self.args[1]
        self.load_profs(logdir, funcmapfile)
        ## Unique nodes list
        self.nodeset = util.node_set(self.profs)
        # Prepare information to add
        self.prepare_registration()
        # DB prepare
        #conn = db.init("postgres", username="kabe", hostname="127.0.0.1")
        self.conn = db.init("sqlite3", dbfile="/home/kabe/Archives/prof.db")
        ### BEGIN TRANSACTION ###
        self.conn.begin_transaction()
        # Register
        try:
            # Profgroup
            group_id = self.add_profgroup()
            # ProfExec Insert
            profexec_id = self.add_profexec(group_id)
            util.out(group_id, profexec_id)
            # Profile Insert
            self.insert_profile(profexec_id)
        except Exception, e:
            util.err("Exception in main", repr(e))
            self.conn.rollback_transaction()
            raise  # Re-raise the exception
        # Finalization
        if self.options.finally_abort:
            self.conn.rollback_transaction()
            self.conn.close()
            if self.options.verbose >= 1:
                util.out("Commit normally aborted")
        else:
            ### COMMIT TRANSACTION ###
            self.conn.commit_transaction()
            self.conn.close()
            if self.options.verbose >= 1:
                util.out("Commit OK")


def main():
    """
    """
    reg = Registerer()
    reg.main()

if __name__ == '__main__':
    #tau.run('main(sys.argv)')
    main()
