-- Merges multiple profexec and shows the average values for each profgroup

CREATE VIEW groupexecmerge
AS
SELECT
    frs.funcname funcname,
    pe.profgroup_id profgroup_id,
    AVG(frs.rank_excl_sum) exec_excl_sum_avg,
    AVG(frs.rank_excl_max) exec_excl_max_avg,
    AVG(frs.rank_excl_min) exec_excl_min_avg,
    AVG(frs.rank_excl_avg) exec_excl_avg_avg,
    AVG(frs.rank_incl_sum) exec_incl_sum_avg,
    AVG(frs.rank_incl_max) exec_incl_max_avg,
    AVG(frs.rank_incl_min) exec_incl_min_avg,
    AVG(frs.rank_incl_avg) exec_incl_avg_avg
FROM funcranksum frs, profexec pe
WHERE frs.profexec_id = pe.id
GROUP BY pe.profgroup_id, frs.funcname
;
