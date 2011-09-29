#!/usr/bin/env python

"""Time Class.
"""


import resource

import modules.struct


class RStopWatch(object):
    """Stopwatch for resource information.
    """
    def _get_rsrc(self):
        return self._rsrc

    rsrc = property(_get_rsrc)

    def __init__(self, ):
        """
        """
        self.__ru1 = None
        self.__ru2 = None

    def __getrusage(self, ):
        """rusage getter wrapper.
        """
        return resource.getrusage(resource.RUSAGE_SELF)

    def start(self, ):
        """Start the stopwatch.
        """
        self.__ru1 = self.__getrusage()

    def stop(self, ):
        """Stop the stopwatch.
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
