#!/usr/bin/env python


"""GXPmake Result Register"""


import sys
import os
import re
import sqlite3

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
import model
import parpdb
import parpdb.dbi


class GXPMakeRegister(object):
    """
    """

    class RegisterException(Exception):
        """Exception representing any failure in registration.
        """

        def __init__(self, ):
            """
            """
            pass

    class DBError(Exception):
        """
        """

        def __init__(self, ):
            """
            """
            pass
    
    def _get_odbc_connection(self):
        return self._DBI.odbc_connection

    odbc_connection = property(_get_odbc_connection)

    def _get_cursor(self):
        return self._cursor

    cursor = property(_get_cursor)

    # Instance Methods

    def __init__(self, odbc_connection):
        """
        """
        self._odbc_connection = odbc_connection
        self._DBI = parpdb.dbi.DBI(odbc_connection)
        self._cursor = self._odbc_connection.cursor()
        self._odbc_connection.autocommit = False

    def process_workflow(self, wf_name):
        """Registers workflow or queries the id.

        If name with wf_name exists returns its id.
        Otherwise inserts a new column and returns the new id.

        @param wf_name Name of workflow
        @return (ID column value with wf_name, True if newly inserted)
        """
        row = self.cursor.execute(
            "SELECT id FROM workflow WHERE name = ?;", wf_name).fetchone()
        if row:
            return int(row[0]), False
        # Record not exists
        self.cursor.execute("INSERT INTO workflow (name) VALUES (?);", wf_name)
        row = self.cursor.execute("SELECT LAST_INSERT_ID();").fetchone()
        if row:
            return int(row[0]), True
        # Fail
        self.odbc_connection.rollback()
        raise RegisterException("Workflow")

    def process_workflow_condition(
        self, filesystem, location, worker_num, input_dataset):
        """Registers workflow_condition.

        @param filesystem file system under which workflow was run
        @param location name of the execution environment
        @param worker_num number of workers
        @param input_dataset name of input dataset
        @return (ID column value with args, True if newly inserted)
        """
        row = self.cursor.execute(
            """
SELECT id
FROM workflow_condition
WHERE
    filesystem = ? AND
    location = ? AND
    worker_num = ? AND
    input_dataset = ?;""",
            filesystem, location, worker_num, input_dataset).fetchone()
        if row:
            return int(row[0]), False
        # Record not exists
        self.cursor.execute("""
INSERT INTO workflow_condition
    (filesystem, location, worker_num, input_dataset)
VALUES (?, ?, ?, ?);""", filesystem, location, worker_num, input_dataset)
        row = self.cursor.execute("SELECT LAST_INSERT_ID();").fetchone()
        if row:
            return int(row[0]), True
        # Fail
        self.odbc_connection.rollback()
        raise RegisterException("Workflow Condition")

    def process_workflow_trial(self, wf_id, wfc_id, startts, elapsed):
        """Registers workflow_trial.

        @param wf_id workflow id
        @param wfc_id workflow condition id
        @param startts start timestamp
        @param elapsed elapsed time
        @return new workflow_trial's ID
        """
        self.cursor.execute("""
INSERT INTO workflow_trial
    (workflow, workflow_condition, start_timestamp, elapsed_time)
VALUES(?, ?, ?, ?);""", wf_id, wfc_id, startts, elapsed)
        row = self.cursor.execute("SELECT LAST_INSERT_ID();").fetchone()
        if row:
            return int(row[0])
        # Fail
        self.odbc_connection.rollback()
        raise RegisterException("Workflow Trial")

    def process_worker(self, trial_id, worker):
        """Process a worker registration.
        
        @param trial_id Workflow trial ID
        @param worker model.Worker instance to register
        """
        print "Register " + str(worker) + " for trial %d" % (trial_id) + \
            "(worker=%s)" % (worker.name)
        self.cursor.execute("""
INSERT INTO wf_worker
    (`index`, workflow_trial_id, name, ncpus, memory)
VALUES(?, ?, ?, ?, ?);""",
                            worker.index, trial_id, worker.name,
                            worker.ncpus, worker.memory)
        row = self.cursor.execute("SELECT LAST_INSERT_ID();").fetchone()
        print row

    def process_application(self, wf_id, appname):
        """Registers application.

        @param wf_id workflow id
        @param application name
        @return (application's ID, New if newly created)
        """
        row = self.cursor.execute("""
SELECT id FROM application
WHERE workflow = ? AND name = ?
""", wf_id, appname).fetchone()
        if row:
            return row[0], False
        self.cursor.execute("""
INSERT INTO application
    (workflow, name)
VALUES(?, ?);""", wf_id, appname)
        row = self.cursor.execute("SELECT LAST_INSERT_ID();").fetchone()
        if row:
            return int(row[0]), True
        # Fail
        self.odbc_connection.rollback()
        raise RegisterException("Application")

    def process_job(self, wf_id, wft_id, app_id, row, appargs):
        """Registers a job.

        @param wf_id workflow id
        @param wft_id workflow trial id
        @param app_id application id
        @param row DictReader-interfaced object
        @param appargs arguments string for application
        @return (job's ID, New if newly created)
        """
        columns = ("workflow",
                   "workflow_trial",
                   "application",
                   "work_idx",
                   "args",
                   "local_pid",
                   "worker",
                   "elapsed_local",
                   "elapsed_remote",
                   "time_user",
                   "time_system",
                   "minor_faults",
                   "major_faults",
                   "local_start_time",
                   "remote_start_time",
                   )
        values = (wf_id,
                  wft_id,
                  app_id,
                  row["work_idx"],
                  appargs,
                  row["pid"],
                  row["man_name"],
                  row["time_since_start"],
                  row["worker_time"],
                  row["utime"],
                  row["stime"],
                  row["minflt"],
                  row["majflt"],
                  row["time_start"],
                  row["worker_time_start"],
                  )
        self.cursor.execute("""
INSERT INTO job (%s)
VALUES(%s);""" % (", ".join(columns),
                  ", ".join(["?" for x in range(len(columns))])),
                            *values)
        row = self.cursor.execute("SELECT LAST_INSERT_ID();").fetchone()
        if row:
            return int(row[0]), True
        # Fail
        self.odbc_connection.rollback()
        raise RegisterException("Job")

    def commit(self, ):
        """Commit transaction.
        """
        self.odbc_connection.commit()

    def rollback(self, ):
        """Rollback transaction.
        """
        self.odbc_connection.rollback()

    # Static

    workerstr_re = re.compile(r"^(?P<worker>.+)-(?P<username>[^-].+)" + \
                                  r"-\d{4}-\d{2}-\d{2}-" + \
                                  r"\d{2}-\d{2}-\d{2}-\d{0,5}$")
    cmd2tuple_re = re.compile(r"^(?P<app>[^\s]+)\s+(?P<args>.+)\s*$")

    @staticmethod
    def workerstr2workername(workerstr):
        """Convert worker string to worker name.

        @param workerstr string of worker

        >>> s = "huscs000-kabe-2011-04-11-00-17-13-10387"
        >>> GXPMakeRegister.workerstr2workername(s)
        'huscs000'
        >>> s = "huscs-charlie-kabe-2011-04-11-00-17-13-3"
        >>> GXPMakeRegister.workerstr2workername(s)
        'huscs-charlie'
        """
        m = GXPMakeRegister.workerstr_re.match(workerstr)
        if m:
            return m.group("worker")

    @staticmethod
    def cmd2tuple(cmdstr):
        """Split command to application and Arguments.

        @param cmdstr command string

        >>> s = "mProjectPP  -X -x 1.01260 " \
                "../../data/data2/2mass-atlas-981204n-j0320080.fits " \
                "p2mass-atlas-981204n-j0320080.fits ../../data/data2/region.hdr"
        >>> trargs = ('-X -x 1.01260 ' + \
                     '../../data/data2/2mass-atlas-981204n-j0320080.fits ' + \
                     'p2mass-atlas-981204n-j0320080.fits ' + \
                     '../../data/data2/region.hdr')
        >>> GXPMakeRegister.cmd2tuple(s).group("app")
        'mProjectPP'
        >>> GXPMakeRegister.cmd2tuple(s).group("args") == trargs
        True
        """
        m = GXPMakeRegister.cmd2tuple_re.match(cmdstr)
        return m


class WFPARPDB(object):
    """O/R Mapper class for Workflow PARP DB.
    """
    def _get_connection(self):
        if not self._accessed_connection:
            self._connection = sqlite3.connect(self.dbfile)
            self._accessed_connection = True
        return self._connection

    def _set_start_ts(self, value):
        self._start_ts = value

    def _get_start_ts(self):
        if not self._accessed_trial:
            self.get_trial_info()
        return self._start_ts

    def _set_elapsed(self, value):
        self._elapsed = value

    def _get_elapsed(self):
        if not self._accessed_trial:
            self.get_trial_info()
        return self._elapsed

    def _get_workers(self):
        if not self._accessed_worker:
            self.get_worker_info()
        return self._workers
    
    def _get_dbfile(self):
        return self._dbfile

    connection = property(_get_connection)
    start_ts = property(_get_start_ts, _set_start_ts)
    elapsed = property(_get_elapsed, _set_elapsed)
    dbfile = property(_get_dbfile)
    workers = property(_get_workers)

    # Flags
    _accessed_trial = False
    _accessed_worker = False
    _accessed_connection = False

    def __init__(self, dbfile):
        """Constructor.

        @param dbfile Path to the Database file
        """
        self._dbfile = dbfile

    def get_trial_info(self, ):
        """Access DB and get information from the "trial" table.
        """
        import datetime
        cursor = self.connection.cursor()
        cursor.execute("""
SELECT start_timestamp, elapsed_time
FROM trial;
""")
        row = cursor.fetchone()
        if row:
            start_ts = datetime.datetime.fromtimestamp(row[0]).isoformat(" ")
            td = datetime.timedelta(seconds=row[1])
            elapsed = "%02d:%02d:%02d.%d" % (
                int(td.seconds / 3600),
                int((td.seconds % 3600) / 60),
                int(td.seconds % 60),
                td.microseconds)
            self.start_ts = start_ts
            self.elapsed = elapsed
            self._accessed_trial = True
            return self
        raise GXPMakeRegister.DBError()

    def get_worker_info(self, ):
        """Access DB and get information from the "worker" table.
        """
        self._workers = []
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
SELECT idx, name, cpu, memory FROM worker ORDER BY idx;
    """)
            for row in cursor:
                w = model.Worker(row[0], row[1], row[2], row[3])
                self._workers.append(w)
        except sqlite3.DatabaseError, e:
            mes = e.message
            raise e
            raise GXPMakeRegister.DBError(mes)
        self._accessed_worker = True


if __name__ == '__main__':
    import doctest
    doctest.testmod()
