"""Daily CSV export handed to billing-svc.

billing-svc/ingest/orders_csv.py reads this file by column POSITION (it was
written before we had headers and nobody has changed it). The header row is
emitted for humans only. Adding, removing or reordering a column here is a
coordinated change with billing -- README "Schema changes".
"""
import csv
import io

from orders.models import ORDER_COLUMNS
from orders.repository import connect, insert_order

# Export columns = ORDER_COLUMNS, in order. Do not reorder.
EXPORT_HEADER = list(ORDER_COLUMNS)


def export_orders(conn, since_iso):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(EXPORT_HEADER)
    rows = conn.execute(
        f"SELECT {', '.join(ORDER_COLUMNS)} FROM orders"
        " WHERE created_at >= ? ORDER BY id",
        (since_iso,),
    )
    for row in rows:
        w.writerow(row)
    return buf.getvalue()


if __name__ == "__main__":
    c = connect()
    insert_order(c, customer_id=7, total_cents=1200)
    insert_order(c, customer_id=8, total_cents=4300, currency="GBP")
    print(export_orders(c, "2000-01-01T00:00:00+00:00"), end="")
