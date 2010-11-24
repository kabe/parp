CREATE TABLE userevent (
    eventname TEXT,
    numevents INTEGER,
    maxtime INTEGER,
    mintime INTEGER,
    mean INTEGER,
    sumsqr INTEGER,
    profgroup_id INTEGER,
    rank INTEGER,
    PRIMARY KEY (profgroup_id, rank, eventname),
    FOREIGN KEY (profgroup_id) REFERENCES profgroup(id)
);
