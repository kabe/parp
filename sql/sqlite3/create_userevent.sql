CREATE TABLE userevent (
    eventname TEXT,
    numevents INTEGER,
    maxtime INTEGER,
    mintime INTEGER,
    mean INTEGER,
    sumsqr INTEGER,
    profexec_id INTEGER,
    rank INTEGER,
    PRIMARY KEY (profexec_id, rank, eventname),
    FOREIGN KEY (profexec_id) REFERENCES profexec(id)
);
