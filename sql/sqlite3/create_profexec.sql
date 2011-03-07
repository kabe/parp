CREATE TABLE profexec (
    id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
    profgroup_id INTEGER,
    exec_time DOUBLE PRECISION NOT NULL,
    display_time DOUBLE PRECISION,
    start_ts INT,
    UNIQUE (profgroup_id, start_ts),
    FOREIGN KEY (profgroup_id) REFERENCES profgroup(id) ON DELETE CASCADE
);
