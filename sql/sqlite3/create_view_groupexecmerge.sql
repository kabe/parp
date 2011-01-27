-- Merges multiple profexec and shows the average values for each profgroup

CREATE VIEW groupexecmerge
AS
SELECT
    frs.funcname funcname,
    pe.profgroup_id profgroup_id,
    AVG(frs.rank_sum) exec_sum_avg,
    AVG(frs.rank_max) exec_max_avg,
    AVG(frs.rank_min) exec_min_avg,
    AVG(frs.rank_avg) exec_avg_avg
FROM funcranksum frs, profexec pe
WHERE frs.profexec_id=pe.id
GROUP BY pe.profgroup_id, frs.funcname
;
