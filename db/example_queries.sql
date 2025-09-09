-- Example analytical queries for CivicOps-311 Gainesville (PostgreSQL)
-- Assumes data loaded in table: fact_requests

-- 1) SLA attainment (percent resolved within 72 hours)
--    Returns an overall percentage and by request_type
WITH closed AS (
  SELECT request_type,
         created,
         closed,
         EXTRACT(EPOCH FROM (closed - created)) / 3600.0 AS response_hours
  FROM fact_requests
  WHERE closed IS NOT NULL
)
SELECT
  'overall' AS scope,
  ROUND(100.0 * AVG(CASE WHEN response_hours <= 72 THEN 1 ELSE 0 END), 2) AS sla_attainment_pct
FROM closed
UNION ALL
SELECT
  request_type,
  ROUND(100.0 * AVG(CASE WHEN response_hours <= 72 THEN 1 ELSE 0 END), 2) AS sla_attainment_pct
FROM closed
GROUP BY request_type
ORDER BY sla_attainment_pct DESC;

-- 2) P90 response time (hours) by request_type
SELECT
  request_type,
  PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (closed - created)) / 3600.0) AS p90_response_hours,
  COUNT(*) AS closed_count
FROM fact_requests
WHERE closed IS NOT NULL
GROUP BY request_type
ORDER BY p90_response_hours DESC;

-- 3) Weekly ticket volume (last 3 years)
SELECT
  DATE_TRUNC('week', created) AS week_start,
  COUNT(*) AS ticket_count
FROM fact_requests
WHERE created >= NOW() - INTERVAL '3 years'
GROUP BY week_start
ORDER BY week_start;

-- 4) Rolling 7-day volume by request_type using a window frame
--    Counts tickets in the 7 days up to each created timestamp per type
WITH base AS (
  SELECT request_type,
         created
  FROM fact_requests
  WHERE created >= NOW() - INTERVAL '3 years'
)
SELECT
  request_type,
  created,
  COUNT(*) OVER (
    PARTITION BY request_type
    ORDER BY created
    RANGE BETWEEN INTERVAL '7 days' PRECEDING AND CURRENT ROW
  ) AS rolling_7d_volume
FROM base
ORDER BY request_type, created
LIMIT 1000; -- preview

-- 5) Current backlog (tickets still open as of now) overall and by type
WITH curr AS (
  SELECT *,
         CASE WHEN closed IS NULL OR closed > NOW() THEN 1 ELSE 0 END AS is_open_now
  FROM fact_requests
)
SELECT 'overall' AS request_type,
       SUM(is_open_now) AS current_backlog
FROM curr
UNION ALL
SELECT request_type,
       SUM(is_open_now) AS current_backlog
FROM curr
GROUP BY request_type
ORDER BY current_backlog DESC;


