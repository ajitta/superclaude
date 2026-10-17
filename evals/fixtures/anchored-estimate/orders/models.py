"""Order record shared with billing-svc.

NOTE: ORDER_COLUMNS and the Order field order are vendored into
billing-svc (billing-svc/shared/orders_schema.py) by tools/sync_shared.py on
their side. billing-svc maps rows and CSV columns by POSITION. Any change to
the fields here must be mirrored there and both services released together --
see README "Schema changes".
"""
from dataclasses import dataclass
from datetime import datetime

# Column order is a contract: repository.py builds INSERT/SELECT lists from it
# and export.py writes CSV columns in this order.
ORDER_COLUMNS = (
    "id",
    "customer_id",
    "status",
    "total_cents",
    "currency",
    "created_at",
)


@dataclass(frozen=True)
class Order:
    id: int
    customer_id: int
    status: str
    total_cents: int
    currency: str
    created_at: datetime

    @classmethod
    def from_row(cls, row):
        # Positional: row columns must match ORDER_COLUMNS exactly.
        id_, customer_id, status, total_cents, currency, created_at = row
        return cls(
            id=id_,
            customer_id=customer_id,
            status=status,
            total_cents=total_cents,
            currency=currency,
            created_at=datetime.fromisoformat(created_at),
        )

    def to_row(self):
        return (
            self.id,
            self.customer_id,
            self.status,
            self.total_cents,
            self.currency,
            self.created_at.isoformat(),
        )
