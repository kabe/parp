CREATE TABLE profile (
    funcname TEXT,
    calls INTEGER,
    subrs INTEGER,
    excl DOUBLE PRECISION,
    incl DOUBLE PRECISION,
    group_s TEXT,
    profgroup_id INTEGER,
    rank INTEGER,
    PRIMARY KEY (profgroup_id, rank, funcname),
    FOREIGN KEY (profgroup_id)  REFERENCES profgroup(id)
);
