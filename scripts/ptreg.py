#!/usr/bin/env python

# This is ***TEST*** script

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
from gxpmake import gxpmake, register
import pyodbc
import tau.db
import config
import config.db
from modules.paratrac import ptimporter


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
    parser.add_option("-p", "--paratrac", dest="paratrac",
                      help="prefix of paratrac databases",
                      metavar="DBS_PREFIX")
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
    """Main routine. ***TEST***

    Registers the database file into the database.
    """
    # Preparation
    options, args = parse_opt()
    datafile, dbfile = None, None
    if args:
        datafile, dbfile = args[0], args[1]
    else:
        datafile = gxpmake.testfile()
    cn = pyodbc.connect(config.db.connect_str)
    reg = register.GXPMakeRegister(cn)
    assert(cn)
    # Registration
    # ParaTrac DB if exists
    if options.paratrac:
        workflow_trial_id = 9999
        print dir(ptimporter.ParaTracImporter)
        paths = ptimporter.ParaTracImporter.expand_globs(options.paratrac)
        print paths
        importer = ptimporter.ParaTracImporter(cn, paths)
        importer.prepare_all()
        importer.register_all(workflow_trial_id)
    # COMMIT
    options.finally_abort = True
    if options.finally_abort:
        reg.rollback()
        print "Abort OK"
    else:
        reg.commit()
        print "Registration OK"


if __name__ == '__main__':
    main()
