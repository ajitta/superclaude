"""All SQL for the orders table. Admin tooling and the API both call this."""
import sqlite3
from datetime import datetime, timezone

from orders.models import ORDER_COLUMNS, Order

_COLS = ", ".join(ORDER_COLUMNS)
_PLACEHOLDERS = ", ".join("?" for _ in ORDER_COLUMNS)


def connect(path=":memory:"):
    conn = sqlite3.connect(path)
    # In prod the schema comes from schema/*.sql applied by ops; this mirrors
    # 001 + 002 so the smoke run works without a database.
    conn.execute(
        "CREATE TABLE IF NOT EXISTS orders ("
        " id INTEGER PRIMARY KEY, customer_id INTEGER NOT NULL,"
        " status TEXT NOT NULL, total_cents INTEGER NOT NULL,"
        " currency TEXT NOT NULL DEFAULT 'USD', created_at TEXT NOT NULL)"
    )
    return conn


def insert_order(conn, customer_id, total_cents, currency="USD"):
    now = datetime.now(timezone.utc).replace(microsecond=0)
    cur = conn.execute(
        f"INSERT INTO orders ({_COLS}) VALUES ({_PLACEHOLDERS})",
        (None, customer_id, "new", total_cents, currency, now.isoformat()),
    )
    conn.commit()
    return cur.lastrowid


def get_order(conn, order_id):
    row = conn.execute(
        f"SELECT {_COLS} FROM orders WHERE id = ?", (order_id,)
    ).fetchone()
    return Order.from_row(row) if row else None


def list_orders_for_customer(conn, customer_id):
    rows = conn.execute(
        f"SELECT {_COLS} FROM orders WHERE customer_id = ? ORDER BY id",
        (customer_id,),
    ).fetchall()
    return [Order.from_row(r) for r in rows]


def set_status(conn, order_id, status):
    conn.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
    conn.commit()


if __name__ == "__main__":
    c = connect()
    oid = insert_order(c, customer_id=42, total_cents=1999)
    insert_order(c, customer_id=42, total_cents=500, currency="EUR")
    print(get_order(c, oid))
    print(len(list_orders_for_customer(c, 42)), "orders for customer 42")
