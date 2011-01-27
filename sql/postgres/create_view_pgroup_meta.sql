-- View pgroup_meta
-- Overview of profile group.
-- Only shows the average time of execution time in the profile group.
CREATE VIEW pgroup_meta AS
SELECT pe.profgroup_id profgroup_id,
       AVG(pe.exec_time) avg_time,
       pg.procs procs,
       (sums.sum2 - sums.sum1 * sums.sum1 / sums.c ) / sums.c var
FROM profexec pe,
     profgroup pg,
     (SELECT profgroup_id pgid,
            SUM(exec_time * exec_time) sum2,
            SUM(exec_time) sum1, COUNT(*) c
      FROM profexec
      GROUP BY profgroup_id) sums
WHERE pe.profgroup_id = pg.id
  AND pg.id = sums.pgid
GROUP BY profgroup_id, pg.procs, sums.sum2, sums.sum1, sums.c
;

-- CREATE VIEW pgroup_meta AS
-- SELECT pe.profgroup_id,
--        AVG(pe.exec_time) avg_time,
--        pg.procs procs
-- FROM profexec pe, profgroup pg
-- WHERE pe.profgroup_id=pg.id
-- GROUP BY profgroup_id, pg.procs
-- ;
