CREATE VIEW mpifuncprofile AS
SELECT *
FROM profile
WHERE funcname LIKE 'MPI_%';
