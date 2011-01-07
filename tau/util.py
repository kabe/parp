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


r_ha8000cluster = re.compile(r"^(?P<batchname>[a-zA-z_])(?P<nodenum>\d+)$")


def hostname2clustername(hostname):
    """Convert hostname to cluster name.

    Arguments:
    - `hostname`: hostname in string
    >>> hostname2clustername("hongo100")
    'hongo'
    >>> hostname2clustername("hongo")
    'hongo'
    >>> hostname2clustername("b201")
    'HA8000-S004'
    >>> hostname2clustername("b205")
    'HA8000-S008'
     """
    m = r_ha8000cluster.match(hostname)
    if m:
        assert(m.group("batchname") == "b")
        if int(m.group("nodenum")) in (201, 202, 203, 204):
            return "HA8000-S004"
        if int(m.group("nodenum")) in (205, 206, 207, 208):
            return "HA8000-S008"
    r = re.compile(r"^([a-zA-Z]+)(\d+)?$")
    m = r.match(hostname)
    return m.groups()[0]


def filename2rank(filename):
    """Pick up the rank of the process.

    Arguments:
    - `filename`:
    """
    #print filename
    r = re.compile(r".*profile\.(\d+)\.(\d+).(\d+)$")
    m = r.match(filename)
    return m.group(1)


def soup2dic(soup, pg_dic):
    """Select values from soup and register them to pg_dic.

    Arguments:
    - `soup`:
    - `pg_dic`:
    Returns:
    - `pg_dic`: modified version of the argument
    - `exec_time`:
    """
    start_time = 0
    end_time = 0
    for attr in soup.findAll("attribute"):
        attrname = attr.find("name").string
        attrvalue = attr.find("value").string
        pg_dic[attrname] = attrvalue
        if attrname == "Executable":
            appname = attrvalue
            pg_dic["application"] = appname
        if attrname == "Hostname":
            cl_name = hostname2clustername(attrvalue)
            pg_dic["place"] = cl_name
        if attrname == "Starting Timestamp":
            start_time = int(attrvalue)
        if attrname == "Timestamp":
            end_time = int(attrvalue)
    pg_dic["exec_time"] = (end_time - start_time) / 1e6
    return pg_dic


def out(s, stream=sys.stdout):
    """Output string to the stream.

    Arguments:
    - `s`:
    """
    stream.write(s)


def err(s, stream=sys.stderr):
    """Output string to the stream especially for error messages.

    Arguments:
    - `s`:
    - `stream`:
    """
    stream.write(s)
    stream.fflush()


def main(argv):
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    main(sys.argv)
