#!/usr/bin/env python


import sys
import pg

import db


class PostgreSQLHandler(object):
    """PostgreSQL Connection Handler.
    """

    def _get_db(self):
        return self._db

    db = property(_get_db)

    def _set_plan_nr(self, value):
        self._plan_nr = value

    def _get_plan_nr(self):
        return self._plan_nr

    plan_nr = property(_get_plan_nr, _set_plan_nr)

    def _prepare(self, q):
        """Prepare a statement with place holder number.

        @param q query to prepare
        >>> import db
        >>> conn = db.init("postgres", username="kabe", hostname="127.0.0.1")
        >>> s = "HOGE ? fuga ? bar ?"
        >>> conn._prepare(s)
        'HOGE $1 fuga $2 bar $3'
        >>> s = "foo ? bar ? baz"
        >>> conn._prepare(s)
        'foo $1 bar $2 baz'
        >>> s = "? foo ? bar ? baz"
        >>> conn._prepare(s)
        '$1 foo $2 bar $3 baz'
        >>> conn.close()
        """
        retstr = ""
        ph_counter = 1
        index = 0
        pos = q[index:].find("?")
        while pos >= 0:
            retstr += q[index: index + pos]
            retstr += "$%d" % (ph_counter,)
            ph_counter += 1
            index += pos + 1
            pos = q[index:].find("?")
        retstr += q[index:]
        return retstr

    def __init__(self, db,):
        """Initialize DB handler.

        @param db PostgreSQL DB object (authenticated)
        """
        self._db = db
        self._plan_nr = 0

    def begin_transaction(self, ):
        """BEGIN TRANSACTION.
        """
        self.db.query("BEGIN TRANSACTION;")

    def commit_transaction(self, ):
        """COMMIT TRANSACTION.
        """
        self.db.query("COMMIT TRANSACTION;")

    def rollback_transaction(self, ):
        """ROLLBACK TRANSACTION.
        """
        sys.stderr.write("Rollback transaction...\n")
        self.db.query("ROLLBACK TRANSACTION;")

    def insert(self, table, idict, **kywds):
        """Insert a column to the database.

        Arguments:
        @param table table to insert a column into
        @param idict dictionary of column data
        @param **kywds additional key-value pairs to insert
        @return the dictionary of the inserted column
        """
        # Additional dictionary
        for k, v in kywds.iteritems():
            idict[k] = v
        try:
            rdic = self.db.insert(table, idict)
        except pg.ProgrammingError, e:
            raise db.ProgrammingError, e
        else:
            return rdic

    def select(self, stmt, phs=None):
        """Issue a select statement.

        @param stmt select statement
        @param phs values for place holders
        @return list of tuples which selected
        """
        if phs:
            return self.query(stmt, phs)
        else:
            return self.query(stmt)

    def get(self, table, arg, keyname=None):
        """Get a row from a database or view.

        @param table
        @param arg
        @param keyname
        """
        if keyname:
            return self.db.get(table, arg, keyname)
        else:
            return self.db.get(table, arg)

    def query(self, q, phs=None):
        """DB.query wrapper.

        @param q Query string
        @param phs values for place holders.
               If specified uses prepared statement
        @return None if insert;
                List of Tuple if select
        """
        if phs:
            prepare_stmt = "PREPARE plan_%d AS %s" % (self.plan_nr, q)
            self.db.query(self._prepare(prepare_stmt))
            d_phs = list()
            for x in phs:
                if isinstance(x, basestring):
                    d_phs.append(str(x))
                else:
                    d_phs.append(x)
            d_phs = tuple(d_phs)
            result = self.db.query("EXECUTE plan_%d %s"
                                   % (self.plan_nr, d_phs))
            self.plan_nr += 1
            if result:
                return result.getresult()
            else:
                return None
        else:
            result = self.db.query(q)
            if result:
                return self.db.query(q).getresult()
            else:
                return None

    def close(self, ):
        """Commit changes and Close the database.
        """
        self.db.close()


if __name__ == '__main__':
    import doctest
    doctest.testmod()
