#!/usr/bin/env python


dbmap = {"sqlite3": 1, "postgres": 2}


class ProgrammingError(Exception):
    pass


def init(dbtype, **kywds):
    """Initialize Database handler.

    * PostgreSQL
      If you want to use PostgreSQL, you must specify at least:
        o kywds.username
        o kywds.hostname
    * SQLite3
      If you want to use PostgreSQL, you must specify at least:
        o kywds.dbfile
    Arguments:
    - `dbtype`: specify the kind of RDBMS
    - `**kywds`: attributes for each RDBMS

    >>> import db
    >>> conn = db.init("sqlite3", dbfile="/home/kabe/Archives/prof.db")
    >>> conn.close()
    >>> conn = db.init("postgres", username="kabe", hostname="127.0.0.1")
    >>> conn.close()
    """
    if dbtype == "sqlite3":
        import sqlite3
        import kp_sqlite3
        conn = sqlite3.connect(kywds["dbfile"])
        return kp_sqlite3.SQLite3Handler(conn)
    elif dbtype == "postgres":
        import pg
        import kp_postgres
        db = pg.DB(kywds["username"], kywds["hostname"])
        return kp_postgres.PostgreSQLHandler(db)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
