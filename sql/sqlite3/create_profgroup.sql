CREATE TABLE profgroup (
    application TEXT,
    nodes INTEGER,
    procs INTEGER,
    place TEXT,
    library TEXT,
    id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
    CONSTRAINT profgroup_unique UNIQUE (application, nodes, procs, place, library)
);
