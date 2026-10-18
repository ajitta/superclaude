CREATE TABLE orders (
    id          bigserial PRIMARY KEY,
    customer_id bigint NOT NULL,
    status      text NOT NULL,
    total       numeric(12, 2) NOT NULL,
    created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE order_items (
    id        bigserial PRIMARY KEY,
    order_id  bigint NOT NULL REFERENCES orders (id),
    sku       text NOT NULL,
    quantity  integer NOT NULL,
    price     numeric(12, 2) NOT NULL
);

CREATE TABLE order_events (
    id         bigserial PRIMARY KEY,
    order_id   bigint NOT NULL REFERENCES orders (id),
    kind       text NOT NULL,
    payload    jsonb NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);
