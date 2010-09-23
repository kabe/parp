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


class Profile(object):
    """Profile Class
    """

    def _set_function(self, value):
        self._function = value

    def _get_function(self):
        return self._function

    function = property(_get_function, _set_function)

    class Prof(object):
        """Profile of a function
        """

        def _set_attr(self, value):
            self._attr = value

        def _get_attr(self):
            return self._attr

        attr = property(_get_attr, _set_attr)

        def __init__(self, mo):
            """
            """
            self.attr = dict()
            for attr in ("funcname", "group"):
                self.attr[attr] = mo.group(attr)
            for attr in ("calls", "subrs", "excl", "incl", "profcalls"):
                self.attr[attr] = float(mo.group(attr))
            self.funcname = self.attr["funcname"]

    def __init__(self, ):
        """Initialisation.
        """
        self.funcname = ""
        self.function = dict()

    def add(self, funcs):
        """Add functions profiles.

        Arguments:
        - `funcs`: arrays of MatchObject for each function
        """
        for f in funcs:
            profobj = Profile.Prof(f)
            self.function[profobj.funcname] = profobj


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
        self.profile = Profile()
        self.userevents = UserEvents()

    def load_all(self, ):
        """Load a file.
        """
        # Open
        self.file = open(self.filename)
        try:
            # Header 1
            line = self.file.readline()
            self.load_header1(line.rstrip())
            # Second XML metadata
            line = self.file.readline()
            self.load_xml(line.rstrip())
            # Functions
            lines = [self.file.readline().rstrip()
                     for i in xrange(self.func_num)]
            self.profile.add(self.load_function(func) for func in lines)
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
        except AttributeError:
            print self.filename
            raise
        finally:
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
                           r"(?P<calls>\d+) (?P<subrs>[\d\.E]+) " + \
                           r"(?P<excl>[\d\.E]+) (?P<incl>[\d\.E]+) " + \
                           r"(?P<profcalls>\d+) " + \
                           r"GROUP=\"(?P<group>.+?)\"")
        m = r.match(line)
        return m

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
                           r"(?P<numevents>[\d\.E]+) " + \
                           r"(?P<max>[\d\.E]+) (?P<min>[\d\.E]+) " + \
                           r"(?P<mean>[\d\.]+) (?P<sumsqr>[\d\.E]+)")
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
