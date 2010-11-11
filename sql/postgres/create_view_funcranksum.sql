CREATE VIEW funcranksum AS
SELECT funcname, profgroup_id, SUM(excl) sum, MAX(excl) max, MIN(excl) min, AVG(excl) avg
FROM funcprofile
GROUP BY funcname, profgroup_id;
