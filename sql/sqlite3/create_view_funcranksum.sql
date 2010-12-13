CREATE VIEW funcranksum AS
SELECT
    funcname,
    profexec_id,
    SUM(excl) rank_sum,
    MAX(excl) rank_max,
    MIN(excl) rank_min,
    AVG(excl) rank_avg
FROM funcprofile
GROUP BY funcname, profexec_id
;

