CREATE TABLE userevent (
    eventname text,
    numevents int,
    maxtime int,
    mintime int,
    mean int,
    sumsqr int,
    profgroup_id int REFERENCES profgroup(id),
    rank int,
    PRIMARY KEY (profgroup_id, rank, eventname)
);
