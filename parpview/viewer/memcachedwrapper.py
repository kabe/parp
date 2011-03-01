#!/usr/bin/env python

class MemcachedConnection(object):
    """
    """

    def __init__(self, use, memcached_servers):
        """Initialize an instance.
        
        @param use if True use memcached
        @param memcached_servers memcached servers list of "127.0.0.1:11211"
        """
        self._use = use
        self._servers = memcached_servers
        memcache_conn = None
        if self._use:
            try:
                import memcache
                memcache_conn = memcache.Client(self._servers)
            except:
                use_memcache = False
        self.conn = memcache_conn

    def get(self, key):
        """Get content of key.

        @param key
        """
        if not self._use:
            return None
        obj = self.conn.get(str(key))
        return obj

    def set(self, key, value):
        """Set content of key as value.

        @param key memcached key
        @param value keyed value
        """
        self.conn.set(str(key), value)

    def flush(self, ):
        """Flush memcached.
        """
        self.conn.flush_all()
    
    def __str__(self, ):
        """str().
        """
        s = "<MemcachedWrapper "
        if not self._use:
            s += "Flag: OFF"
        else:
            s += """Server="%s" """ % (str(self._servers))
        s += ">"
        return s
