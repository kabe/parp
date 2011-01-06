-- View pgroup_meta
-- Overview of profile group.
-- Only shows the average time of execution time in the profile group.
CREATE VIEW pgroup_meta AS
SELECT pe.profgroup_id,
       AVG(pe.exec_time) avg_time,
       pg.procs procs
FROM profexec pe, profgroup pg
WHERE pe.profgroup_id=pg.id
GROUP BY profgroup_id, pg.procs
;
