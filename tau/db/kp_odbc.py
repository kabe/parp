import pyodbc


class ODBCHandler(object):
    """ODBC Connection Handler.
    """

    # Properties
    def _set_conn(self, value):
        self._conn = value

    def _get_conn(self):
        return self._conn

    conn = property(_get_conn, _set_conn)

    def _set_cursor(self, value):
        self._cursor = value

    def _get_cursor(self):
        return self._cursor

    cursor = property(_get_cursor, _set_cursor)

    # Constructor
    def __init__(self, conn_string):
        """
        """
        self.conn = pyodbc.connect(conn_string)
        self.cursor = conn.cursor()

    # Private Methods

    # Public Methods
