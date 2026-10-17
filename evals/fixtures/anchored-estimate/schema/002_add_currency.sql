-- 002: add currency (expand phase).
--
-- Release notes from when this shipped:
--   * 002a (this file) added the column nullable. orders-svc 1.14 wrote it,
--     billing-svc 3.2 learned to read it. Both deployed Thu release window.
--   * 002b (next release) backfilled 'USD' and set NOT NULL + DEFAULT.
--   * ORDER_COLUMNS / Order.from_row / EXPORT_HEADER all changed in 1.14,
--     and billing's positional CSV reader had to move one index. We broke
--     the export once in staging because the header change went out before
--     billing's reader did.
ALTER TABLE orders ADD COLUMN currency TEXT;

-- 002b, applied one release later:
-- UPDATE orders SET currency = 'USD' WHERE currency IS NULL;
-- ALTER TABLE orders ALTER COLUMN currency SET NOT NULL;
-- ALTER TABLE orders ALTER COLUMN currency SET DEFAULT 'USD';
