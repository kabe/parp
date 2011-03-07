-- View pgroup_meta
-- Overview of profile group.
-- Only shows the average time of execution time in the profile group.
CREATE VIEW pgroup_meta AS
SELECT pe.profgroup_id profgroup_id,
       AVG(pe.exec_time) avg_time,
       AVG(pe.display_time) avg_dtime,
       pg.procs procs,
       (sums.sum2 - sums.sum1 * sums.sum1 / sums.c ) / sums.c var,
       (sums.sum_d2 - sums.sum_d1 * sums.sum_d1 / sums.c ) / sums.c dvar
FROM profexec pe,
     profgroup pg,
     (SELECT profgroup_id pgid,
            SUM(exec_time * exec_time) sum2,
            SUM(exec_time) sum1,
            SUM(display_time * display_time) sum_d2,
            SUM(display_time) sum_d1,
            COUNT(*) c
      FROM profexec
      GROUP BY profgroup_id) sums
WHERE pe.profgroup_id = pg.id
  AND pg.id = sums.pgid
GROUP BY profgroup_id, pg.procs
;
