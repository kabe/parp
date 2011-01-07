#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Insert all records into the database
#

import sys
import os
import os.path
import re

import db

from TauLoad.Loader import Loader
import nm.loader

## regex for cluster environment
cluster_re = re.compile(r"^(?P<cname>[a-zA-Z]+)(?P<nodenum>\d+)?$")
## regex for HA8000 supercomputer
r_ha8000cluster = re.compile(r"^(?P<batchname>[a-zA-z_])(?P<nodenum>\d+)$")


def getplacename(options, infodic):
    """Convert hostname to cluster name.

    @param options command-line options
    @param infodic dictionary containing all information
    """
    hostname = infodic["soupdic"]["Node Name"]
    m = r_ha8000cluster.match(hostname)
    if m:
        assert(m.group("batchname") == "b")
        if int(m.group("nodenum")) in (201, 202, 203, 204):
            return "HA8000-S004"
        if int(m.group("nodenum")) in (205, 206, 207, 208):
            return "HA8000-S008"
    else:
        return hostname2clustername(hostname)
    return m.groups()[0]


def hostname2clustername(hostname):
    """Convert hostname to cluster name.

    @param hostname host name

    >>> hostname2clustername("hongo100")
    'hongo'
    >>> hostname2clustername("hongo")
    'hongo'
    >>> hostname2clustername("b201")
    'HA8000-S004'
    >>> hostname2clustername("b205")
    'HA8000-S008'
    """
    m = cluster_re.match(hostname)
    return m.group("cname")


def filename2rank(filename):
    """Pick up the rank of the process.

    @param filename
    """
    r = re.compile(r".*profile\.(\d+)\.(\d+).(\d+)$")
    m = r.match(filename)
    return m.group(1)


def soup2dic(soup):
    """Select values from soup and register them to pg_dic.

    @param soup beautifulsoup XML soup
    @return dictionary of key-value in the metadata XML
    """
    sdic = dict()
    for attr in soup.findAll("attribute"):
        attrname = attr.find("name").string
        attrvalue = attr.find("value").string
        sdic[attrname] = attrvalue
    return sdic


def out(*s, **kwrds):
    """Output string to the stream.

    @param *s object to print
    @param **kwrds kwrds["stream"] is output stream
    """
    stream = sys.stdout
    if "stream" in kwrds:
        stream = kwrds["stream"]
    if len(s) == 1:
        s = s[0]
    print >> stream, s


def err(*s, **kwrds):
    """Output string to the stream especially for error messages.

    @param *s object to print
    @param **kwrds kwrds["stream"] is output stream
    """
    stream = sys.stderr
    if "stream" in kwrds:
        stream = kwrds["stream"]
    if len(s) == 1:
        s = s[0]
    print >> stream, s
    stream.flush()


def main(argv):
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    main(sys.argv)
