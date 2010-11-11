CREATE TABLE funcmap (
    funcname text,
    addr int,
    application text,
    PRIMARY KEY (application, funcname)
);
