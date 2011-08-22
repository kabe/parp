#!/usr/bin/env python

import sys
import os
import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
from gxpmake import gxpmake, register
import pyodbc
import config
import config.db
from modules import postscript


# Figure Options
class FigureOption:
    NODE_INTERVAL = 5
    X_WIDTH = 500
    Y_OFFSET = 100


class ManInfo(object):
    """Man's information to produce postscript.
    """

    def _get_position(self):
        return self._position

    def _get_name(self):
        return self._name

    def _get_index(self):
        return self._index

    position = property(_get_position)
    name = property(_get_name)
    index = property(_get_index)

    def __init__(self, index, name, position):
        """
        """
        self._index = index
        self._name = name
        self._position = position


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
                      action="store_true", default=False,
                      help="finally abort (thus no side-effect)")
    parser.add_option("-t", "--trial", dest="trial",
                      help="trial number",
                      metavar="TRIAL")
    (options, args) = parser.parse_args()
    if args:
        pass
    if not options.trial:
        parser.error("Specify condition number")
    return options, args


def main():
    """Main routine.

Generate timechart of the specified trial.
    """
    records, workers, meta, apps = prepare_data()
    # Determine x axis and y axis
    # X-axis: time from 0 to End of the run
    # Y-axis: worker sorted
    psd = []
    # Create Inverted Index
    iindex = {}
    for idx, man in enumerate(workers):
        p = postscript.Position(
            0,
            (len(workers) - idx) * FigureOption.NODE_INTERVAL + \
                FigureOption.Y_OFFSET)
        m = ManInfo(index=idx, name=man, position=p)
        iindex[man] = m
    # Init
    psd.extend(postscript.begin())
    # Create colour chart for applications
    apps_colour_d = mk_apps_colourd(apps)
    psd.extend(postscript.place_colourlegend(
            apps_colour_d,
            postscript.Position(200, 0),
            postscript.Position(100, 90)))
    # Max name length of workers
    max_worker_length = max(len(man) for man in workers)
    # Place Axis
    origin_x = max_worker_length * 0.5 * postscript.FONT_SIZE
    origin = postscript.Position(
        origin_x,
        FigureOption.Y_OFFSET)
    rt_y = FigureOption.Y_OFFSET + \
        FigureOption.NODE_INTERVAL * (len(workers) + 2)
    rt = postscript.Position(origin_x + FigureOption.X_WIDTH, rt_y)
    psd.extend(postscript.draw_axis(origin, rt))
    # Place grid
    psd.extend(postscript.place_grid(
            origin_x + FigureOption.X_WIDTH,
            rt_y))
    # Place Node index
    for idx, man in enumerate(workers):
        m = iindex[man]
        psd.extend(postscript.place_text(
                man, postscript.Position(0, m.position.y)))
    # Place boxes
    records_time_max = max(
        [record.starttime + record.elapsedtime for record in records])
    maximum_time = max(records_time_max, meta.time)
    #print >>sys.stderr, maximum_time, records_time_max, meta.time
    TIMESCALE = (1.0 * FigureOption.X_WIDTH) / maximum_time
    #print >>sys.stderr, meta
    #print >>sys.stderr, "origin_x=%f X_WIDTH=%f" % (
    #    origin_x, FigureOption.X_WIDTH,)
    for idx, record in enumerate(records):
        m = iindex[record.worker]
        x0 = postscript.Position(
            origin_x + TIMESCALE * record.starttime,
            m.position.y)
        size = postscript.Position(
            TIMESCALE * record.elapsedtime,
            FigureOption.NODE_INTERVAL)
        try:
            assert(x0.x + size.x - 0.01 <= origin_x + FigureOption.X_WIDTH)
        except AssertionError, e:
            print >>sys.stderr, "x0.x=%f size.x=%f idx=%d" % (x0.x, size.x, idx)
            print >>sys.stderr, "starttime=%f elapsedsec=%f" % (
                record.starttime, record.elapsedtime)
        psd.extend(
            postscript.draw_rect_size(x0, size, apps_colour_d[record.appname]))
    # Finalize
    psd.extend(postscript.finalize())
    print postscript.NL.join(psd)


def prepare_data():
    # Class
    class Meta(object):
        """Meta info of the trial.
        """
        def _set_name(self, value):
            self._name = value

        def _get_name(self):
            return self._name

        def _set_workers(self, value):
            self._workers = value

        def _get_workers(self):
            return self._workers

        def _set_time(self, value):
            self._time = value

        def _get_time(self):
            return self._time

        name = property(_get_name, _set_name)
        workers = property(_get_workers, _set_workers)
        time = property(_get_time, _set_time)

        def __init__(self, name, workers, time):
            """Initializer

            @param name Workflow Name
            @param workers Number of workers
            @param time Execution time of the trial
            """
            self.name = name
            self.workers = workers
            self.time = time

        def __repr__(self, ):
            """
            """
            s = "<Meta object name=%s workers=%d time=%f>" % (
                self.name, self.workers, self.time)
            return s

    # Preparation
    options, args = parse_opt()
    cn = pyodbc.connect(config.db.connect_str)
    cursor = cn.cursor()
    # Here trial number is specified.
    ## Records for each tasks
    res = None
    sql = """
SELECT
  app.name appname,
  job.worker worker,
  job.local_start_time starttime,
  job.elapsed_local elapsedtime
FROM
  workflow_trial wft,
  job job,
  application app
WHERE
  job.workflow_trial = wft.id
 AND
  job.application = app.id
 AND
  wft.id = ?
"""
    res = cursor.execute(sql, (options.trial,)).fetchall()
    ## Workers list
    sql = """
SELECT DISTINCT
  job.worker worker
FROM job
WHERE
  job.workflow_trial = ?
"""
    workers = cursor.execute(sql, (options.trial,)).fetchall()
    # shrink workers list
    workers = sorted([w[0] for w in workers])
    ## Trial metadata
    meta = None
    sql = """
SELECT
  wf.name name,
  wfc.worker_num workers,
  TIME_TO_SEC(wft.elapsed_time) time
FROM
  workflow wf,
  workflow_trial wft,
  workflow_condition wfc
WHERE
  wf.id = wft.workflow
 AND
  wfc.id = wft.workflow_condition
 AND
  wft.id = ?
"""
    meta = cursor.execute(sql, (options.trial,)).fetchone()
    m = Meta(meta.name, meta.workers, meta.time)
    ## Applications list
    sql = """
SELECT
  DISTINCT app.name appname
FROM
  application app,
  workflow_trial wft,
  job job
WHERE
  job.application = app.id
 AND
  wft.id = job.workflow_trial
 AND
  wft.id = ?
"""
    apps = [rec.appname
            for rec in cursor.execute(sql, (options.trial,)).fetchall()]
    # Assertion
    if not res or not workers:
        raise Exception("Preparation of data failed.")
    return (res, workers, m, apps)


def mk_apps_colourd(apps):
    """Make applications colour dictionary in CMYK.

    @param apps dictionary from application name to the colour
    """
    d = {}  # To-be-returned dictionary
    n = len(apps)
    c0 = [1, 0, 0, 0]
    c1 = [0, 0, 1, 0]
    for idx, app in enumerate(apps):
        c = [0] * len(c0)
        for cel in range(len(c0)):
            c[cel] = (
                1.0 * idx * c0[cel] + (n - 1.0 - idx) * c1[cel]) / (n - 1.0)
        d[app] = c
    #print >>sys.stderr, d
    return d


if __name__ == '__main__':
    main()
