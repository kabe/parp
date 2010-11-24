#!/usr/bin/env python


class SQLite3Handler(object):
    """SQLite3 Connection Handler.
    """

    def _get_conn(self):
        return self._conn

    conn = property(_get_conn)

    def _get_cur(self):
        return self._cur

    cur = property(_get_cur)

    def __init__(self, conn):
        """Initialize DB handler.

        Arguments:
        - `conn`: SQLite3 connection object
        """
        self._conn = conn
        self._cur = self._conn.cursor()

    def insert(self, table, idict, **kywds):
        """Insert a column to the database.
        Returns dictionary of the iniserted column.

        Arguments:
        - `table`: table to insert a column into
        - `idict`: dictionary of column data
        - `**kywds`:
        """
        # Additional dictionary
        for k, v in kywds.iteritems():
            idict[k] = v
        # SQL w/ Place holder
        sql = "INSERT INTO %s (%s) VALUES (%s)" % (
            table,
            ", ".join(idict.keys()),
            ", ".join(("?", ) * len(idict)))
        #print sql
        #print idict
        self.cur.execute(sql, idict.values())
        # Get last inserted column
        lastrowid = self.cur.lastrowid
        last_get_sql = ("SELECT * FROM %s " + \
            "WHERE ROWID='%d'") % (table, lastrowid)
        rcursor = self.cur.execute(last_get_sql)
        rcolumn = rcursor.fetchone()
        rcnames = [c[0] for c in rcursor.description]
        return dict(zip(rcnames, rcolumn))

    def close(self, ):
        """Commit changes and Close the database.
        """
        self.conn.commit()
        self.cur.close()
