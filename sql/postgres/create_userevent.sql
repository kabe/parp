CREATE TABLE userevent (
    eventname text,
    numevents int,
    maxtime int,
    mintime int,
    mean int,
    sumsqr int,
    profexec_id int REFERENCES profexec(id),
    rank int,
    PRIMARY KEY (profexec_id, rank, eventname)
);
