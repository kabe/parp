#!/usr/bin/env python


class Worker():
    """Worker Class.
    """
    def _get_index(self):
        return self._index

    def _get_name(self):
        return self._name

    def _get_ncpus(self):
        return self._ncpus

    def _get_memory(self):
        return self._memory

    index = property(_get_index)
    name = property(_get_name)
    ncpus = property(_get_ncpus)
    memory = property(_get_memory)

    def __init__(self, index, name, ncpus, memory):
        """Constructor.
        """
        self.index = index
        self.name = name
        self.ncpus = ncpus
        self.memory = memory

    def __repr__(self, ):
        """Representation form.

        Too long name will be abbreviated to first 10 characters.
        """
        name_repr = self.name if len(self.name) < 10 else self.name[:10] + "..."
        s = "<Worker instance index=%d ncpus=%d memory=%d name='%s'>"
        return s % (self.index, self.ncpus, self.memory, name_repr)


class Record(object):
    """Record of an application.
    """

    _dic = {}

    def __getattr__(self, attr):
        """Transaparent accessor to _dic
        
        @param attr attribute name
        >>> r = Record(a="b", c="d")
        >>> r.a
        'b'
        >>> r.c
        'd'
        >>> r.e
        Traceback (most recent call last):
        ...
        KeyError: 'e'
        """
        return self._dic[attr]

    def __init__(self, **dic):
        """Constructor.

        @param **dic dictionary of attributes
        >>> r = Record(a="b", c="d")
        """
        for k, v in dic.iteritems():
            self._dic[k] = v


if __name__ == '__main__':
    import doctest
    doctest.testmod()
