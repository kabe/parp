CREATE VIEW pgroup_ratio AS
SELECT gem.funcname funcname,
       gem.profgroup_id profgroup_id,
       gem.exec_excl_avg_avg excl_pe_rank_avg,
       gem.exec_incl_avg_avg incl_pe_rank_avg,
       gem.exec_excl_max_avg excl_pe_rank_max_avg,
       gem.exec_incl_max_avg incl_pe_rank_max_avg,
       gem.exec_excl_min_avg excl_pe_rank_min_avg,
       gem.exec_incl_min_avg incl_pe_rank_min_avg,
       (gem.exec_excl_avg_avg / pgm.avg_time / 1000000) excl_avg_ratio,
       (gem.exec_incl_avg_avg / pgm.avg_time / 1000000) incl_avg_ratio,
       (gem.exec_excl_max_avg / pgm.avg_time / 1000000) excl_max_ratio,
       (gem.exec_incl_max_avg / pgm.avg_time / 1000000) incl_max_ratio,
       (gem.exec_excl_min_avg / pgm.avg_time / 1000000) excl_min_ratio,
       (gem.exec_incl_min_avg / pgm.avg_time / 1000000) incl_min_ratio
FROM groupexecmerge gem,
     pgroup_meta pgm
WHERE gem.profgroup_id = pgm.profgroup_id
;
