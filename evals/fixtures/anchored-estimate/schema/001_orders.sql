-- 001: initial orders table
CREATE TABLE orders (
    id          BIGSERIAL PRIMARY KEY,
    customer_id BIGINT      NOT NULL,
    status      TEXT        NOT NULL,
    total_cents BIGINT      NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX orders_customer_id_idx ON orders (customer_id);

-- billing-svc reads this table with role billing_ro. Keep in sync with
-- billing-svc/shared/orders_schema.py (see orders/models.py).
GRANT SELECT ON orders TO billing_ro;
