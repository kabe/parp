#!/usr/bin/env python


import sys
import os
import os.path
import re

import yaml

path = os.path.join(os.environ["HOME"], "git/prof/tau/")
if path not in sys.path:
    sys.path.append(path)
import db

import util


class displaytimeUpdator(object):
    """Update display_time column in profexec by reading function.yaml
    """
    def _get_function_yaml(self):
        return self._function_yaml

    function_yaml = property(_get_function_yaml)

    def updatedtime(self, peid, appname, procs, appinfo):
        """Update display_time infor for an application.

        @param self
        @param peid
        @param appname
        @param procs
        @param appinfo
        """
        update_sql = """
UPDATE profexec
SET
    display_time = ?
WHERE id = ?;
"""
        dtime = self.calc_display_time(peid, appname, procs, appinfo)
        self.conn.query(update_sql, (dtime, peid))

    def calc_display_time(self, peid, appname, procs, appinfo):
        """Calcurate a display_time for an application.

        @param self
        @param peid
        @param appname
        @param procs
        @param appinfo
        """
        getfunc_sql = """
SELECT funcname,
       profexec_id,
       rank,
       excl
FROM profile
WHERE profexec_id = ?;
"""
        rtup = self.conn.select(getfunc_sql, (peid,))
        display_time = 0
        function_names = appinfo.keys()
        for row in rtup:
            funcname, peid, rank, time = row
            if funcname in function_names:
                display_time += time
        display_time /= 1e6
        display_time /= procs
        return display_time

    def __init__(self, function_yaml):
        """Constructor.

        @param function_yaml YAML object for function map.
        """
        self._function_yaml = function_yaml
        self.conn = db.init("sqlite3", dbfile="/home/kabe/Archives/prof.db")

    def update(self, ):
        """Update main.
        """
        pes = self.get_peinfo()
        for pe in pes:
            peid, appname, procs = pe
            appinfo = self.function_yaml[appname]
            #print appname, appinfo
            self.updatedtime(peid, appname, procs, appinfo)

    def get_peinfo(self, ):
        """Get information of (profexec_id, app_viewname).
        """
        sql = """
SELECT
    pe.id pe_id,
    pg.app_viewname name,
    pg.procs procs
FROM profgroup pg, profexec pe
WHERE pg.id = pe.profgroup_id
"""
        rtup = self.conn.select(sql, ())
        return rtup

def main():
    yaml_path = "../../parpview/viewer/e9n/function.yaml"
    with open(yaml_path) as f:
        yaml_str = f.read()
        y = yaml.load(yaml_str)
    updator = displaytimeUpdator(y)
    updator.update()


if __name__ == '__main__':
    main()

