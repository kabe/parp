#!/usr/bin/env python


import sys
import sqlite3

import db


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

        @param conn SQLite3 connection object
        """
        self._conn = conn
        self._cur = self._conn.cursor()

    def begin_transaction(self, ):
        """BEGIN TRANSACTION.
        """
        self.conn.execute("BEGIN TRANSACTION;")

    def commit_transaction(self, ):
        """COMMIT TRANSACTION.
        """
        self.conn.execute("COMMIT TRANSACTION;")

    def rollback_transaction(self, ):
        """ROLLBACK TRANSACTION.
        """
        sys.stderr.write("Rollback transaction...\n")
        try:
            self.conn.execute("ROLLBACK TRANSACTION;")
        except:
            pass

    def insert(self, table, idict, **kywds):
        """Insert a column to the database.

        @param table table to insert a column into
        @param idict dictionary of column data
        @param **kywds
        @return dictionary of the iniserted column
        """
        # Additional dictionary
        for k, v in kywds.iteritems():
            idict[k] = v
        # SQL w/ Place holder
        sql = "INSERT INTO %s (%s) VALUES (%s)" % (
            table,
            ", ".join(idict.keys()),
            ", ".join(("?", ) * len(idict)))
        try:
            self.cur.execute(sql, idict.values())
        except sqlite3.IntegrityError, e:
            raise db.ProgrammingError, e
        except Exception, e:
            print "Unknown insert error", e
            raise
        # Get last inserted column
        lastrowid = self.cur.lastrowid
        last_get_sql = "SELECT * FROM %s WHERE ROWID=?" % (table)
        rcursor = self.cur.execute(last_get_sql, (lastrowid, ))
        rcolumn = rcursor.fetchone()
        rcnames = [c[0] for c in rcursor.description]
        return dict(zip(rcnames, rcolumn))

    def select(self, stmt, phs=None):
        """Issue a select statement.

        @param stmt select statement
        @param phs values for place holders
        @param list of tuples which selected
        """
        if phs:
            r = self.query(stmt, phs)
        else:
            r = self.query(stmt)
        return r

    def get(self, table, arg, keyname=None):
        """Get a row from a database or view.

        @param table
        @param arg
        @param keyname
        @return ?
        """
        pass

    def query(self, q, args=()):
        """Issue a query.

        @param q Query string (place holder "?" may appear)
        @param *args Place holder string
        @return None if q is insert statement;
                list of tuples if q is select statement
        """
        c = self.conn.cursor()
        cur = c.execute(q, args)
        r = cur.fetchall()
        # Not completed yet
        if r:
            return r
        else:
            return r  # Maybe it's OK

    def close(self, ):
        """Commit changes and Close the database.
        """
        self.conn.commit()
        self.cur.close()


if __name__ == '__main__':
    import doctest
    doctest.testmod()
