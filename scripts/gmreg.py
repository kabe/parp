#!/usr/bin/env python

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
from gxpmake import gxpmake, register
import pyodbc
import tau.db
import config
import config.db


def parse_opt():
    """Parse Command Line Arguments.
    """
    from optparse import OptionParser
    usage = "Usage: %prog [options] WORK_TXT WORK_DB"
    parser = OptionParser(usage=usage, version="%prog " + config.version)
    parser.add_option("-v", "--verbose", dest="verbose",
                      action="count", default=0,
                      help="verbose output (more -v shows more output)")
    parser.add_option("-b", "--abort", dest="finally_abort",
                      action="store_true", default=False,
                      help="finally abort (thus no side-effect)")
    parser.add_option("-l", "--location", dest="location",
                      help="specify execution location",
                      default="",
                      metavar="LOCATION")
    parser.add_option("-n", "--worker-num", dest="worker_num",
                      help="number of workers",
                      metavar="WORKER_NUM")
    parser.add_option("-i", "--input-dataset", dest="input_dataset",
                      help="input dataset name",
                      metavar="INPUT_DATASET")
    parser.add_option("-f", "--filesystem", dest="filesystem",
                      help="filesystem",
                      default="",
                      metavar="FILESYSTEM")
    parser.add_option("-w", "--workflow", dest="workflow_name",
                      help="name of workflow",
                      metavar="WORKFLOW")
    (options, args) = parser.parse_args()
    if args:
        if len(args) != 2:
            parser.error("incorrect number of arguments: run with -h")
    if not options.workflow_name:
        parser.error("workflow name must be specified")
    if not options.worker_num:
        parser.error("worker # not specified")
    return options, args


def main():
    """Main routine.

Registers the database file into the database.
    """
    # Preparation
    options, args = parse_opt()
    datafile, dbfile = None, None
    if args:
        datafile, dbfile = args[0], args[1]
    else:
        datafile = gxpmake.testfile()
    gmdb = gxpmake.GxpMakeDB(datafile)
    cn = pyodbc.connect(config.db.connect_str)
    reg = register.GXPMakeRegister(cn)
    workparpdb = register.WFPARPDB(dbfile)
    assert(cn)
    # Registration
    # TABLE WORKFLOW
    workflow_name = options.workflow_name
    workflow_id, isnew = reg.process_workflow(workflow_name)
    print "Workflow ID = %d, New: %s" % (workflow_id, str(isnew))
    # TABLE WORKFLOW_CONDITION
    workflow_condition_id, isnew = reg.process_workflow_condition(
        options.filesystem,
        options.location,
        options.worker_num,
        options.input_dataset)
    print "Workflow Condition ID = %d, New: %s" % (
        workflow_condition_id, str(isnew))
    # TABLE WORKFLOW_TRIAL (Always new)
    start_timestamp, elapsed_time = workparpdb.start_ts, workparpdb.elapsed
    print start_timestamp, elapsed_time
    workflow_trial_id = reg.process_workflow_trial(
        workflow_id, workflow_condition_id, start_timestamp, elapsed_time)
    print "WorkflowTrial ID = %d" % (workflow_trial_id)
    ## Workers
    for w in workparpdb.workers:
        reg.process_worker(workflow_trial_id, w)
    ## For each job
    for row in gmdb.csvreader:  # row has an inteface of csv.DictReader
        # TABLE APPLICATION
        appmatch = register.GXPMakeRegister.cmd2tuple(row["cmd"])
        application_id, isnew = reg.process_application(
            workflow_id, appmatch.group("app"))
        if options.verbose > 1:
            print "Application ID = %d, New: %s" % (application_id, str(isnew))
        # TABLE JOB
        job_id, isnew = reg.process_job(workflow_id,
                                 workflow_trial_id,
                                 application_id,
                                 row,
                                 appmatch.group("args"))
        if options.verbose > 1:
            print "Job ID = %d, New: %s" % (job_id, str(isnew))
        # TODO: prepare data for metric
        # TABLE METRIC
    # COMMIT
    if options.finally_abort:
        reg.rollback()
        print "Abort OK"
    else:
        reg.commit()
        print "Registration OK"


if __name__ == '__main__':
    main()
