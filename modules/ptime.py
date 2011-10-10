#!/usr/bin/env python

"""Time Class.
"""


import resource
import time as builtin_time

import modules.struct


class RStopWatch(object):
    """Stopwatch for resource information.
    """
    def _get_rsrc(self):
        return self._rsrc

    rsrc = property(_get_rsrc)

    def __init__(self, ):
        """
        >>> rsw = RStopWatch()
        """
        self.__ru1 = None
        self.__ru2 = None

    def __getrusage(self, ):
        """rusage getter wrapper.

        >>> rsw = RStopWatch()
        >>> isinstance(rsw._RStopWatch__getrusage(), resource.struct_rusage)
        True
        """
        return resource.getrusage(resource.RUSAGE_SELF)

    def start(self, ):
        """Start the stopwatch.

        >>> rsw = RStopWatch()
        >>> rsw.start()
        """
        self.__ru1 = self.__getrusage()

    def stop(self, ):
        """Stop the stopwatch.

        >>> rsw = RStopWatch()
        >>> rsw.start()
        >>> rsw.stop()
        >>> isinstance(rsw.rsrc.utime, float)
        True
        """
        self.__ru2 = self.__getrusage()
        self.__calc_diff()

    def __calc_diff(self, ):
        """Calculate the resource difference and store.
        """
        r1 = self.__ru1
        r2 = self.__ru2
        rdiff = RDiff()
        for x in range(len(r1)):
            rdiff[x] = r2[x] - r1[x]
        self._rsrc = rdiff


class RDiff(modules.struct.Struct):
    """Stores the difference information of resources.
    """

    def __init__(self, ):
        """
        """
        super(self.__class__, self).__init__()
        self.setfields(["utime", "stime",
                        "maxrss", "ixrss", "idrss", "isrss",
                        "minflt", "maxflt", "nswap",
                        "inblock", "outblock",
                        "msgsnd", "msgrcv",
                        "nsignals", "nvcsw", "nivcsw"])


class StopWatch(object):
    """Normal Stopwatch.
    """
    def _set_laps(self, value):
        self._laps = value

    def _get_laps(self):
        return self._laps

    laps = property(_get_laps, _set_laps)

    def _set_is_running(self, value):
        self._is_running = value

    def _get_is_running(self):
        return self._is_running

    is_running = property(_get_is_running, _set_is_running)

    def __init__(self, ):
        """
        """
        self._laps = []
        self._is_running = False
        self.ts = 0

    def _gettime(self, ):
        """Get time.

        >>> sw = StopWatch()
        >>> isinstance(sw._gettime(), float)
        True
        """
        return builtin_time.time()

    def start(self, ):
        """Start the stopwatch.

        >>> sw = StopWatch()
        >>> sw.start()
        >>> sw.is_running
        True
        """
        self.is_running = True
        self.ts = self._gettime()

    def stop(self, ):
        """Stop the stopwatch.

        >>> sw = StopWatch()
        >>> sw.start()
        >>> sw.stop()
        >>> sw.is_running
        False
        """
        assert(self.is_running)
        self.is_running = False
        t = self._gettime() - self.ts
        self.laps.append(t)

    def second(self, index=0):
        """Time of index-th lap.

        @param index
        >>> sw = StopWatch()
        >>> sw.start()
        >>> sw.stop()
        >>> isinstance(sw.second(), float)
        True
        >>> isinstance(sw.second(0), float)
        True
        >>> isinstance(sw.second(-1), float)
        True
        >>> sw.second(-1) == sw.second()
        True
        >>> sw.second(-1) == sw.second(0)
        True
        """
        return self.laps[index]

    def total_second(self, ):
        """Total time in second.

        >>> sw = StopWatch()
        >>> sw.start()
        >>> sw.stop()
        >>> isinstance(sw.total_second(), float)
        True
        """
        return sum(self.laps)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
