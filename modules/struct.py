#!/usr/bin/env python


"""Generic struct module.
"""


class Struct(object):
    """Generic structure.

    Override this class when you use this class and call #setfields
    in the object constructor.
    """

    def __init__(self, ):
        """
        """
        self._fields = []
        self._dic = {}

    def __len__(self, ):
        """length interface.
        """
        return len(self._fields)

    def __getitem__(self, index):
        """Iterative interface.

        @param index get index(should be positive integer)
        """
        pname = self._fields[index]
        return self._dic[pname]

    def __setitem__(self, index, value):
        """Index setter.

        @param index
        @param value
        """
        pname = self._fields[index]
        self._dic[pname] = value

    def __getattr__(self, pname):
        """Attribute accessor.

        @param pname property name
        """
        if not pname.startswith("_"):
            return self._dic[pname]
        else:
            return object.__getattribute__(self, pname)

    def __setattr__(self, pname, value):
        """Attribute setter.

        @param pname property name
        @param value value to set
        """
        if not pname.startswith("_"):
            self._dic[pname] = value
        else:
            object.__setattr__(self, pname, value)

    def setfields(self, fields):
        """set fields of the structure.

        @param fields
        """
        self._fields = fields
        self._dic = {}
        for f in fields:
            self._dic[f] = None
