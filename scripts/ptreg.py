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
    usage = "Usage: %prog [options]"
    parser = OptionParser(usage=usage, version="%prog " + config.version)
    parser.add_option("-v", "--verbose", dest="verbose",
                      action="count", default=0,
                      help="verbose output (more -v shows more output)")
    parser.add_option("-b", "--abort", dest="finally_abort",
                      action="store_true", default=True,
                      help="finally abort" \
                          " (thus no side-effect, Enabled by default)")
    parser.add_option("-p", "--paratrac", dest="paratrac",
                      help="prefix of paratrac databases",
                      metavar="DBS_PREFIX")
    parser.add_option("-d", "--workflow-trial-id", dest="wt_id",
                      help="workflow trial's id",
                      metavar="WORKFLOW_TRIAL_ID")
    (options, args) = parser.parse_args()
    return options, args


def import_paratrac(cn, reg, workflow_trial_id, paratrac_prefix):
    """Import ParaTrac database.

    @param cn Main DB Connection
    @param reg GXPMake Register Object
    @param workflow_trial_id Primary Key ID of Table workflow_trial
    @param paratrac_prefix ParaTrac databases glob string
    """
    print dir(ptimporter.ParaTracImporter)
    paths = ptimporter.ParaTracImporter.expand_globs(paratrac_prefix)
    print paths
    importer = ptimporter.ParaTracImporter(cn, paths)
    importer.prepare_all()
    importer.register_all(workflow_trial_id)


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
    cn = pyodbc.connect(config.db.connect_str)
    reg = register.GXPMakeRegister(cn)
    assert(cn)
    # Registration
    workflow_trial_id = 9999
    if options.wt_id:
        workflow_trial_id = options.wt_id
    paratrac_prefix = options.paratrac
    # ParaTrac DB if exists
    if options.paratrac:
        import_paratrac(cn, reg, workflow_trial_id, paratrac_prefix)
    # COMMIT
    if options.finally_abort:
        reg.rollback()
        print "Abort OK"
    else:
        reg.commit()
        print "Registration OK"


if __name__ == '__main__':
    main()
