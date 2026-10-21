import csv
import io

FIELDS = ["id", "customer", "total"]


def to_csv(rows):
    out = io.StringIO()
    w = csv.DictWriter(out, fieldnames=FIELDS)
    w.writeheader()
    w.writerows(rows)
    return out.getvalue()
