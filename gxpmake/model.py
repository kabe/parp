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
        """
        """
        name_repr = self.name if len(self.name) < 10 else self.name[:10] + "..."
        s = "<Worker instance index=%d ncpus=%d memory=%d name='%s'>"
        return s % (self.index, self.ncpus, self.memory, name_repr)
