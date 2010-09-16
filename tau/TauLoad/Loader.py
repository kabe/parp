#!/usr/bin/env python

#
# TauLoader.Loader
#

import re
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup

import Util


class UserEvents(object):
    """
    """

    # Count: # of user events
    def _set_count(self, value):
        self._count = value

    def _get_count(self):
        return self._count

    count = property(_get_count, _set_count)

    # Columns: column tuple
    def _set_columns(self, value):
        c = value.split()
        self._columns = tuple(c[1:])

    def _get_columns(self):
        return self._columns

    columns = property(_get_columns, _set_columns)

    def __init__(self, ):
        """
        """
        pass


class Loader(object):
    """
    """

    def _get_filename(self):
        return self._filename

    filename = property(_get_filename)

    def _set_file(self, value):
        self._file = value

    def _get_file(self):
        return self._file

    file = property(_get_file, _set_file)

    def __init__(self, filename):
        """

        Arguments:
        - `filename`: File name of profile data.
        """
        self._filename = filename
        self.userevents = UserEvents()

    def load_all(self, ):
        """Load a file.
        """
        # Open
        self.file = open(self.filename)
        # TODO: try
        # Header 1
        line = self.file.readline()
        self.load_header1(line.rstrip())
        # Second XML metadata
        line = self.file.readline()
        self.load_xml(line.rstrip())
        # Functions
        function_profiles = [self.file.readline().rstrip()
                             for i in xrange(self.func_num)]
        print function_profiles
        [self.load_function(func) for func in function_profiles]
        # Misc Info
        lines = [self.file.readline().rstrip() for i in xrange(2)]
        self.load_miscinfo(lines)
        # TODO: there seems only "0 aggregates" for now. if error, check.
        # UserEvents
        cols = self.file.readline().rstrip()
        self.userevents.columns = cols
        lines = [self.file.readline().rstrip()
                 for i in xrange(self.userevents.count)]
        self.load_userevents(lines)
        # TODO: finally
        # Close
        self.file.close()
        self.file = None

    def load_header1(self, line):
        """Load the first line in the header.

        Arguments:
        - `line`: line of first line in the profile file.

        >>> loader = Loader("testcase/profile.0.0.0")
        >>> loader.load_header1("102 templated_functions_MULTI_TIME")
        >>> loader.func_num
        102
        """
        r = re.compile(r"(?P<num>\d+) templated_functions_MULTI_TIME")
        m = r.match(line)
        self.func_num = int(m.group("num"))

    def load_xml(self, line):
        """Load XML profile metadata.

        Arguments:
        - `line`:
        """
        columns_str, metaxml = Util.sharp_div(line)
        self.columns = columns_str.split(" ")
        self.soup = BeautifulStoneSoup(metaxml)

    def load_function(self, line):
        """Parse function profile of one line.

        Expectation: Name Calls Subrs Excl Incl ProfileCalls

        Arguments:
        - `line`:

        >>> loader = Loader("testcase/profile.0.0.0")
        >>> loader.load_function(
        ...        "\\"hoge => fuga\\" 3 4 5 6 7 GROUP=\\"TAU | HOGE\\"")
        """
        r = re.compile(r"\"(?P<funcname>.+?)\" " + \
                           r"(?P<calls>\d+) (?P<subrs>\d+) " + \
                           r"(?P<excl>\d+) (?P<incl>\d+) " + \
                           r"(?P<profcalls>\d+) " + \
                           r"GROUP=\"(?P<group>.+?)\"")
        m = r.match(line)
        print m.groups()

    def load_miscinfo(self, lines):
        """Load Miscelloneous information.

        3 aggregates
        26 userevents

        Arguments:
        - `lines`: arrays of two lines like above

        >>> loader = Loader("testcase/profile.0.0.0")
        >>> loader.load_miscinfo(['3 aggregates', '26 userevents'])
        >>> loader.aggregates
        3
        >>> loader.userevents.count
        26
        """
        # Common regexp
        r = re.compile(r"^(?P<num>\d+) \w+$")
        aggr = int(r.match(lines[0]).group("num"))
        uevs = int(r.match(lines[1]).group("num"))
        self.aggregates = aggr  # TODO: maybe to be fixed
        self.userevents.count = uevs

    def load_userevents(self, lines):
        """Load All userevents lines.

        # eventname numevents max min mean sumsqr

        Arguments:
        - `lines`: arrays of lines with userevents information
        """
        r = re.compile(r"\"(?P<eventname>.+?)\" " + \
                           r"(?P<numevents>\d+) " + \
                           r"(?P<max>\d+) (?P<min>\d+) " + \
                           r"(?P<mean>[\d\.]+) (?P<sumsqr>\d+)")
        self.userevents.events = [r.match(line).groups() for line in lines]
        assert(len(self.userevents.events) == self.userevents.count)

    def _test(self, ):
        """
        """
        import doctest
        doctest.testmod()

if __name__ == '__main__':
    # doctest
    loader = Loader("testcase/profile.0.0.0")
    loader._test()
