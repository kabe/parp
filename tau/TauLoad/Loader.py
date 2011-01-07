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

    ## dictionary of function name: metrics
    function = property(_get_function, _set_function)

    class Prof(object):
        """Profile for a function.
        """

        def _set_attr(self, value):
            self._attr = value

        def _get_attr(self):
            return self._attr

        ## dictionary of metrics
        attr = property(_get_attr, _set_attr)

        def __init__(self, mo, funcmap):
            """
            @param mo match object
            @param funcmap function2addr map
            """
            self.attr = dict()
            # funcname
            self.attr["funcname"] = Util.repl_func(mo.group("funcname"),
                                                   funcmap)
            # group
            self.attr["group"] = mo.group("group")
            #for attr in ("funcname", "group"):
            #    self.attr[attr] = mo.group(attr)
            for attr in ("calls", "subrs", "excl", "incl", "profcalls"):
                self.attr[attr] = float(mo.group(attr))
            ## function name
            self.funcname = self.attr["funcname"]

    def __init__(self, ):
        """Initialisation.
        """
        self.function = dict()

    def add(self, funcs, funcmap):
        """Add functions profiles.

        @param funcs arrays of MatchObject for each function
        @param funcmap function2addr map
        """
        for f in funcs:
            profobj = Profile.Prof(f, funcmap)
            self.function[profobj.funcname] = profobj


class Loader(object):
    """
    """

    def _get_filename(self):
        return self._filename

    ## file name of the loader profile
    filename = property(_get_filename)

    def _set_file(self, value):
        self._file = value

    def _get_file(self):
        return self._file

    ## file object of the loader
    file = property(_get_file, _set_file)

    def _get_funcmap(self):
        return self._funcmap

    ## function map for the loader
    funcmap = property(_get_funcmap)

    def __init__(self, filename, funcmap):
        """
        @param filename File name of profile data.
        @param funcmap Function map loader object.
        """
        self._filename = filename
        self._funcmap = funcmap
        ## function profile data
        self.profile = Profile()
        ## userevent profile data
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
            self.profile.add((self.load_function(func) for func in lines),
                             self.funcmap)
            # Misc Info
            lines = [self.file.readline().rstrip() for i in xrange(2)]
            self.load_miscinfo(lines)
            ## @todo there seems only "0 aggregates" for now. if error, check.
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

        @param line line of first line in the profile file.

        >>> import nm.loader
        >>> mloader = nm.loader.Loader("testcase/solver_mpi_tau_pdt.map")
        >>> mloader.load_all()
        >>> loader = Loader("testcase/profile.0.0.0", mloader)
        >>> loader.load_header1("102 templated_functions_MULTI_TIME")
        >>> loader.func_num
        102
        """
        r = re.compile(r"(?P<num>\d+) templated_functions_MULTI_TIME")
        m = r.match(line)
        ## the number of functions in the profile
        self.func_num = int(m.group("num"))

    def load_xml(self, line):
        """Load XML profile metadata.

        @param line
        """
        columns_str, metaxml = Util.sharp_div(line)
        ## the list of columns
        self.columns = columns_str.split(" ")
        ## BeautifulStoneSoup object of the metadata XML
        self.soup = BeautifulStoneSoup(metaxml)

    def load_function(self, line):
        """Parse function profile of one line.

        Expectation: Name Calls Subrs Excl Incl ProfileCalls

        @param line

        Returns MatchObject

        >>> import nm.loader
        >>> mloader = nm.loader.Loader("testcase/solver_mpi_tau_pdt.map")
        >>> mloader.load_all()
        >>> loader = Loader("testcase/profile.0.0.0", mloader)
        >>> m = loader.load_function(
        ...            "\\"hoge => fuga\\" 3 4 5 6 7 GROUP=\\"TAU | HOGE\\"")
        >>> m.group("excl")
        '5'
        >>> m = loader.load_function(
        ...            "\\"hoge => fuga \\" 3 4.0 5.0 6 7 " + \\
        ...            "GROUP=\\"TAU | HOGE\\"")
        >>> m.group("funcname")
        'hoge => fuga'
        >>> m.group("subrs")
        '4.0'
        >>> m.group("excl")
        '5.0'
        >>> m.group("incl")
        '6'
        >>> m = loader.load_function(
        ...            "\\"hoge => fuga\\" 3 4 5.0E6 6.3E7 7 " + \\
        ...            "GROUP=\\"TAU | HOGE\\"")
        >>> m.group("excl")
        '5.0E6'
        >>> m.group("incl")
        '6.3E7'
        """
        r = re.compile(r"\"(?P<funcname>.+?)\s*\" " + \
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

        @param lines arrays of two lines like above

        >>> import nm.loader
        >>> mloader = nm.loader.Loader("testcase/solver_mpi_tau_pdt.map")
        >>> mloader.load_all()
        >>> loader = Loader("testcase/profile.0.0.0", mloader)
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
        ## the number of aggregates
        self.aggregates = aggr  # TODO: maybe to be fixed
        self.userevents.count = uevs

    def load_userevents(self, lines):
        """Load All userevents lines.

        # eventname numevents max min mean sumsqr

        @param lines arrays of lines with userevents information
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
    import nm.loader
    maploader = nm.loader.Loader("testcase/solver_mpi_tau_pdt.map")
    maploader.load_all()
    loader = Loader("testcase/profile.0.0.0", maploader)
    loader._test()
