CREATE TABLE profexec (
    id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
    profgroup_id INTEGER,
    FOREIGN KEY (profgroup_id) REFERENCES profgroup(id)
);
