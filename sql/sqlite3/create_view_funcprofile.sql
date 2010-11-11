-- View for TABLE profile

CREATE VIEW funcprofile AS
SELECT *
FROM profile
WHERE group_s = 'MPI' OR group_s = 'TAU_DEFAULT';
