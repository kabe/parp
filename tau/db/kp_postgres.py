#!/usr/bin/env python


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
        - `**kywds`:
        """
        # Additional dictionary
        for k, v in kywds.iteritems():
            idict[k] = v
        rdic = self.db.insert(table, idict)
        return rdic

    def close(self, ):
        """Commit changes and Close the database.
        """
        self.db.close()
