-- Maintains an execution of an application

CREATE TABLE profexec (
    id SERIAL PRIMARY KEY UNIQUE,
    profgroup_id int REFERENCES profgroup(id),
    exec_time DOUBLE PRECISION NOT NULL
);
