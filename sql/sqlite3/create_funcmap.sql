CREATE TABLE funcmap (
    funcname TEXT,
    addr INTEGER,
    application TEXT,
    PRIMARY KEY (application, funcname)
);
