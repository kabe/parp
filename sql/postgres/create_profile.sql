CREATE TABLE profile (
    funcname text,
    calls int,
    subrs int,
    excl double precision,
    incl double precision,
    group_s text,
    profgroup_id int REFERENCES profgroup(id),
    rank int,
    PRIMARY KEY (profgroup_id, rank, funcname)
);
