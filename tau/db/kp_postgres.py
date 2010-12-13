#!/usr/bin/env python


import pg

import db

class PostgreSQLHandler(object):
    """PostgreSQL Connection Handler.
    """

    def _get_db(self):
        return self._db

    db = property(_get_db)

    def __init__(self, db,):
        """Initialize DB handler.

        Arguments:
        - `db`: PostgreSQL DB object (authenticated)
        """
        self._db = db

    def insert(self, table, idict, **kywds):
        """Insert a column to the database.
        Returns dictionary of the iniserted column.

        Arguments:
        - `table`: table to insert a column into
        - `idict`: dictionary of column data
        - `**kywds`: additional key-value pairs to insert
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

    def select(self, stmt):
        """Issue a select statement.
        
        Arguments:
        - `stmt`: select statement
        """
        return self.db.query(stmt)

    def get(self, table, arg, keyname=None):
        """Get a row from a database or view.
        
        Arguments:
        - `table`:
        - `arg`:
        - `keyname`:
        """
        if keyname:
            return self.db.get(table, arg, keyname)
        else:
            return self.db.get(table, arg)

    def query(self, q):
        """DB.query wrapper
        
        Arguments:
        - `q`: Query string
        """
        result = self.db.query(q)
        if result:
            return self.db.query(q).dictresult()
        else:
            return None

    def close(self, ):
        """Commit changes and Close the database.
        """
        self.db.close()
