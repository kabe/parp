#!/usr/bin/env python


class DBI(object):
    """DB Interface.
    """
    def _get_odbc_connection(self):
        return self._odbc_connection
    
    odbc_connection = property(_get_odbc_connection)

    def __init__(self, odbc_connection):
        """Initialize DBI.
        
        Arguments:
        - `odbc_connection`:
        """
        self._odbc_connection = odbc_connection

    def remove_row_in_table_of(self, tablename, where_clause, params):
        """Execute "DELETE" statement.

        @param tablename Name of Table to delete rows
        @param where_clause "WHERE" clause which can include "?" as parameters
        @param params parameters to hand to the SQL.
        """
        sql = "DELETE FROM %s WHERE %s"
        self.odbc_connection.execute(sql, *params)
