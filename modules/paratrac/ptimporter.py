#!/usr/bin/env python


import sys
import sqlite3
import glob


class ImporterException(Exception):
    """
    """

    def __init__(self, ):
        """
        """
        pass


class ParaTracImporter(object):
    """ParaTrac Information Importer.
    """

    def _set_dbfiles(self, value):
        self._dbfiles = value

    def _get_dbfiles(self):
        return self._dbfiles

    def _set_conn(self, value):
        self._conn = value

    def _get_conn(self):
        return self._conn

    def _set_slaves(self, value):
        self._slaves = value

    def _get_slaves(self):
        return self._slaves

    def _set_verbose(self, value):
        self._verbose = value

    def _get_verbose(self):
        return self._verbose

    dbfiles = property(_get_dbfiles, _set_dbfiles)
    conn = property(_get_conn, _set_conn)
    slaves = property(_get_slaves, _set_slaves)
    verbose = property(_get_verbose, _set_verbose)

    def __init__(self, conn, dbfiles, verbose=0):
        """Constructor.

        @param conn Connection to the main database
        @param dbfiles list of DB file names
        @param verbose verbosity (0 for most silent)
        >>> pti = ParaTracImporter(None, [])
        """
        self._conn = conn
        self._dbfiles = dbfiles
        self._slaves = []
        self._verbose = verbose

    def prepare_all(self, ):
        """Prepare the all slave databases.
        """
        for dbfile in self.dbfiles:
            self.slaves.append(ParaTracDB(dbfile, self.verbose))

    def register_all(self, workflow_trial_id):
        """Register all data.

        @param workflow_trial_id
        """
        for slave in self.slaves:
            slave.connect()
            if self.verbose > 0: print slave.hostname
            # Runtime
            if self.verbose > 1: print slave.runtime
            runtime_value_tp = (
                workflow_trial_id,
                int(slave.runtime["pid"]),
                int(slave.runtime["uid"]),
                int(slave.runtime["gid"]),
                str(slave.runtime["cmdline"]),
                str(slave.runtime["mountpoint"]),
                str(slave.runtime["hostname"]),
                float(slave.runtime["start"]),
                float(slave.runtime["end"]), )
            self.conn.execute("""
INSERT INTO `paratrac_runtime` (
`workflow_trial_id`,
`pid`, `uid`, `gid`,
`cmdline`, `mountpoint`, `hostname`,
`start_ts`, `end_ts`
)
VALUES (
?,
?, ?, ?,
?, ?, ?,
?, ?
);
""", runtime_value_tp)
            row = self.conn.execute("SELECT LAST_INSERT_ID();").fetchone()
            if not row:
                raise ImporterException("Cannot salvage iid")
            iid = int(row[0])
            c = self.conn.cursor()
            sc = slave.conn.cursor()
            # File
            file_sql = """
SELECT iid, fid, path FROM file;
"""
            sc.execute(file_sql)
            fileinsert_sql = """
INSERT INTO paratrac_file (
fid, path, paratrac_iid, workflow_trial_id
)
VALUES (
?, ?, ?, ?
);
"""
            for row in sc:
                _iid, fid, path = int(row[0]), int(row[1]), str(row[2])
                if self.verbose > 1: print slave.hostname, iid, fid, path, workflow_trial_id
                c.execute(fileinsert_sql,
                          (fid, path, iid, workflow_trial_id))
            # Syscalls
            sysc_sql = """
SELECT
 iid, stamp, pid, sysc, fid, res, elapsed, aux1, aux2
FROM sysc;
"""
            syscinsert_sql = """
INSERT INTO paratrac_syscall (
paratrac_iid, workflow_trial_id,
stamp, sysc, pid,
fid, res, elapsed,
aux1, aux2
)
VALUES (
?, ?,
?, ?, ?,
?, ?, ?,
?, ?
);
"""
            sc.execute(sysc_sql)
            for row in sc:
                stamp, pid, sysc, fid, res, elapsed, aux1, aux2 = (
                    float(row[1]), int(row[2]), int(row[3]), int(row[4]),
                    int(row[4]), float(row[5]), int(row[6]), int(row[7]))
                try:
                    c.execute(syscinsert_sql, (
                            iid, workflow_trial_id,
                            stamp, sysc, pid,
                            fid, res, elapsed,
                            aux1, aux2))
                except:
                    raise
            slave.disconnect()

    @staticmethod
    def expand_globs(paths):
        """Expand glob of paths.

        @param paths original paths including *
        """
        return glob.glob(paths)


class ParaTracDB(object):
    """ParaTrac Database connection object.
    """
    def _set_dbfile(self, value):
        self._dbfile = value

    def _get_dbfile(self):
        return self._dbfile

    def _set_conn(self, value):
        self._conn = value

    def _get_conn(self):
        return self._conn

    def _set_runtime(self, value):
        self._runtime = value

    def _get_runtime(self):
        if not self._runtime:
            self.load_runtime()
        return self._runtime

    def _set_hostname(self, value):
        self._hostname = value

    def _get_hostname(self):
        if not self._hostname:
            self.load_runtime()
        return self._hostname

    def _set_verbose(self, value):
        self._verbose = value

    def _get_verbose(self):
        return self._verbose

    dbfile = property(_get_dbfile, _set_dbfile)
    conn = property(_get_conn, _set_conn)
    runtime = property(_get_runtime, _set_runtime)
    hostname = property(_get_hostname, _set_hostname)
    verbose = property(_get_verbose, _set_verbose)

    def __init__(self, dbfile, verbose=0):
        """Initializer.

        @param dbfil filename of the database
        @param verbose verbose (0 for most silent)
        """
        self._dbfile = dbfile
        self._verbose = verbose
        self._conn = None
        self._runtime = None
        self._hostname = None

    def connect(self, ):
        """Connect to the database.
        """
        self.conn = sqlite3.connect(self.dbfile)

    def disconnect(self, ):
        """disconnect the connection.
        """
        self.conn.close()

    def load_runtime(self, ):
        """Get runtime information.

        The "runtime" table structure is
        - item TEXT
        - value TEXT
        """
        runtime = {}
        cur = self.conn.cursor()
        cur.execute("""SELECT * FROM runtime""")
        for row in cur:
            k = row[0]  # item
            v = row[1]  # value
            runtime[k] = v
            if k == "hostname":
                self.hostname = v
        self.runtime = runtime


if __name__ == '__main__':
    import doctest
    doctest.testmod()
