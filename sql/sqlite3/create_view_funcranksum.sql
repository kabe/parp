CREATE VIEW funcranksum AS
SELECT
    funcname,
    profexec_id,
    SUM(excl) rank_excl_sum,
    MAX(excl) rank_excl_max,
    MIN(excl) rank_excl_min,
    AVG(excl) rank_excl_avg,
    SUM(incl) rank_incl_sum,
    MAX(incl) rank_incl_max,
    MIN(incl) rank_incl_min,
    AVG(incl) rank_incl_avg
FROM funcprofile
GROUP BY funcname, profexec_id
;

