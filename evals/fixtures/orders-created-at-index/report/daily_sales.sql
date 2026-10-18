-- Daily sales for one UTC day; the reporting cron binds :day (YYYY-MM-DD) to yesterday.
SELECT count(*) AS orders,
       round(sum(amount), 2) AS revenue
FROM orders
WHERE date(created_at) = :day;
