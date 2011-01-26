CREATE VIEW pgroup_ratio AS
SELECT gem.funcname,
       gem.profgroup_id,
       (gem.exec_avg_avg/pgm.avg_time/1000000) ratio
FROM groupexecmerge gem,
     pgroup_meta pgm
WHERE gem.profgroup_id = pgm.profgroup_id
;
