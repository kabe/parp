CREATE TABLE profile (
    funcname TEXT,
    calls INTEGER,
    subrs INTEGER,
    excl DOUBLE PRECISION,
    incl DOUBLE PRECISION,
    group_s TEXT,
    profexec_id INTEGER,
    rank INTEGER,
    PRIMARY KEY (profexec_id, rank, funcname),
    FOREIGN KEY (profexec_id)  REFERENCES profexec(id)
);
