-- Maintains an execution of an application

CREATE TABLE profexec (
    id SERIAL PRIMARY KEY,
    profgroup_id INT REFERENCES profgroup(id) ON DELETE CASCADE,
    exec_time DOUBLE PRECISION NOT NULL,
    display_time DOUBLE PRECISION,
    start_ts BIGINT,
    UNIQUE (profgroup_id, start_ts)
);
