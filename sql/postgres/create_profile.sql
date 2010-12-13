-- Maintains a profile for each function and each execution

CREATE TABLE profile (
    funcname text,
    calls int,
    subrs int,
    excl double precision,
    incl double precision,
    group_s text,
    profexec_id int REFERENCES profexec(id),
    rank int,
    PRIMARY KEY (profexec_id, rank, funcname)
);
