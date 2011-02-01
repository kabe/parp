CREATE TABLE profgroup (
    application text,
    nodes int,
    procs int,
    place text,
    library text,
    id SERIAL PRIMARY KEY UNIQUE,
    CONSTRAINT profgroup_unique UNIQUE (application, nodes, procs, place, library)
);
