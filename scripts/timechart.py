#!/usr/bin/env python

import sys
import os
import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
from gxpmake import gxpmake, register
import gxpmake.model
from gxpmake.model import Record
import pyodbc
import config
import config.db
from modules import postscript, colour
import tau.util


# Figure Options
class FigureOption:
    NODE_INTERVAL = 5
    X_WIDTH = 500
    Y_OFFSET = 100


class ManInfo(gxpmake.model.Worker):
    """Man's information to produce postscript.
    """

    def _get_position(self):
        return self._position

    def _set_position(self, position):
        self._position = position

    def _get_records(self):
        return self._records

    def _get_slots(self):
        return self._slots

    # size should be the number of CPUs
    slots = property(_get_slots)
    # List of all records on the man
    records = property(_get_records)
    # Position of the man name
    position = property(_get_position, _set_position)

    def __init__(self, index, name, ncpus, memory, position=None):
        """
        """
        #gxpmake.model.Worker.__init__(self, index, name, ncpus, memory)
        super(self.__class__, self).__init__(index, name, ncpus, memory)
        self._position = position
        self._records = []
        self._slots = [[] for x in xrange(self.ncpus)]

    def __repr__(self, ):
        """Representation of Man.
        """
        name_repr = self.name if len(self.name) < 10 else self.name[:10] + "..."
        s = "<Maninfo index=%d ncpus=%d name='%s' records=%d>"
        return s % (self.index, self.ncpus, name_repr, len(self.records))
    
    def setup_slots(self, ):
        """Determine where to place rectangles, without overlapping.
        """
        # This array contains the last timestamp for each cpu slot
        last_cpu_time = [0.0] * self.ncpus
        cpu_index = 0
        counter = 0
        for record in self.records:
            inslot_ok = False
            # Try to add process in the CPU indexed
            first_cpu_index = (cpu_index) % self.ncpus
            # loop index array
            lia = [x for x in xrange(len(self.slots))]
            lia = lia[first_cpu_index:len(lia)] + lia[0:first_cpu_index]
            for cpu_index in lia:
                if last_cpu_time[cpu_index] > record.start_time:
                    continue
                counter += 1
                self.slots[cpu_index].append(record)
                last_cpu_time[cpu_index] = record.start_time + record.elapsed
                inslot_ok = True
                break
            if not inslot_ok:
                # Unfortunately the placement without overlapping failed.
                # Here I choose to append an additional slot.
                self.slots.append([record])
                last_cpu_time.append(record.start_time + record.elapsed)
                tau.util.err("Warning: Not in slot Man=%d Record=%f-%f" % (
                        self.index, record.start_time, record.elapsed))


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
        parser.error("Specify trial number")
    return options, args


def main():
    """Main routine.

Generate timechart of the specified trial.
    """
    options, args, records, workers, meta, apps = prepare_data()
    # Determine x axis and y axis
    # X-axis: time from 0 to End of the run
    # Y-axis: worker sorted
    psd = []
    ########################################
    ###  Data Preparation                ###
    ########################################
    # Create Inverted Index
    iindex = {}
    for man in workers:
        idx = man.index
        iindex[man.name] = man
    for record in records:
        m = iindex[record.worker]
        m.records.append(record)
    for man in workers:
        man.setup_slots()
    if options.verbose > 0:
        tau.util.err("Worker Information:")
        tau.util.err(workers)
    # Assertion
    try:
        assert(sum(len(m.records) for m in workers) ==
               sum(sum(len(s) for s in m.slots) for m in workers))
    except AssertionError, e:
        tau.util.err("sum(workers.m.records)=%d sum(workers.m.slots)=%d" % (
                sum(len(m.records) for m in workers),
                sum(sum(len(s) for s in m.slots) for m in workers)))
        raise e
    ########################################
    ###  Graph Draw                      ###
    ########################################
    for iman in xrange(len(workers)):  # Not pythonic but necessary
        man = workers[iman]
        nr_slots_below = sum(len(m.slots) for m in workers if m.index > iman)
        nr_slots_my = len(man.slots) - 1
        man_y = FigureOption.Y_OFFSET + \
            (nr_slots_below + nr_slots_my) * FigureOption.NODE_INTERVAL
        p = postscript.Position(0, man_y)
        man.position = p
    # Init
    psd.extend(postscript.begin())
    # Create colour chart for applications
    apps_colour_d = mk_apps_colourd(apps)
    psd.extend(postscript.place_colourlegend(
            apps_colour_d,
            postscript.Position(200, 0),
            postscript.Position(100, 90)))
    # Max name length of workers
    max_worker_length = max(len(man.name) for man in workers)
    # Sum of #slots
    nr_slots = sum(len(man.slots) for man in workers)
    # Place Axis
    origin_x = max_worker_length * 0.5 * postscript.FONT_SIZE
    origin = postscript.Position(
        origin_x,
        FigureOption.Y_OFFSET)
    rt_y = FigureOption.Y_OFFSET + \
        FigureOption.NODE_INTERVAL * (nr_slots + 2)
    rt = postscript.Position(origin_x + FigureOption.X_WIDTH, rt_y)
    psd.extend(postscript.draw_axis(origin, rt))
    if options.verbose > 1:
        tau.util.err("Axis: origin=(%f, %f)" % (
                origin_x, FigureOption.Y_OFFSET))
        tau.util.err("Rect: dst=(%f, %f)" % (
                origin_x + FigureOption.X_WIDTH, rt_y))
    # Place grid
    psd.extend(postscript.place_grid(
            origin_x + FigureOption.X_WIDTH,
            rt_y))
    # Place Node index
    for man in workers:
        m = iindex[man.name]
        psd.extend(postscript.place_text(
                man.name, postscript.Position(0, m.position.y)))
    # Calc timescale: for outline box
    records_time_max = max(
        [record.start_time + record.elapsed for record in records])
    maximum_time = max(records_time_max, meta.time)
    TIMESCALE = (1.0 * FigureOption.X_WIDTH) / maximum_time
    # Place boxes For each worker
    for man in workers:
        for islot, slot in enumerate(man.slots):
            y = man.position.y - islot * FigureOption.NODE_INTERVAL
            for record in slot:
                x = origin_x + TIMESCALE * record.start_time
                x0 = postscript.Position(x, y)
                colourinfo = apps_colour_d[record.appname]
                size = postscript.Position(
                    TIMESCALE * record.elapsed,
                    FigureOption.NODE_INTERVAL)
                psd.extend(
                    postscript.draw_rect_size(x0, size, colourinfo))
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
ORDER BY
  job.local_start_time
"""
    res = cursor.execute(sql, (options.trial,)).fetchall()
    #cursor.execute(sql, (options.trial,))
    #records = [Record(appname=r[0], worker=r[1], start_time=r[2], elapsed=r[3])
    #           for r in cursor]
    records = []
    for row in res:
        r = Record(appname=row.appname, worker=row.worker,
                   start_time=row.starttime, elapsed=row.elapsedtime)
        records.append(r)
    ## Workers list
    sql = """
SELECT DISTINCT
  `index`, name, ncpus, memory
FROM wf_worker
WHERE
  wf_worker.workflow_trial_id = ?
ORDER BY
  `index`
"""
    cursor.execute(sql, (options.trial,))
    workers = [ManInfo(row[0], row[1], row[2], row[3]) for row in cursor]
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
    if not records:
        raise Exception("Preparation of data failed: records None.")
    if not workers:
        raise Exception("Preparation of data failed: workers None.")
    return (options, args, records, workers, m, apps)


def mk_apps_colourd(apps):
    """Make applications colour dictionary in CMYK.

    @param apps dictionary from application name to the colour
    """
    d = {}  # To-be-returned dictionary
    n = len(apps)
    c0 = colour.cmyk(1, 0, 0, 0)
    c1 = colour.cmyk(0, 0, 1, 0)
    colours = colour.yuv_gradation(n, c0, c1)
    d = dict(zip(apps, colours))
    #print >>sys.stderr, d
    return d


if __name__ == '__main__':
    main()
