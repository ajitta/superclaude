# ORD-731: Delivery instructions on orders

**Requested by:** Support
**Priority:** Normal

Customers keep emailing us things like "leave at side door" or "call on
arrival" after they have already checked out, and support has nowhere to put
that text. We want a free-text **delivery instructions** field (max 500 chars)
on each order.

Acceptance criteria:

1. Support can set delivery instructions on an existing order from the admin
   script (`orders/repository.py` is what the admin tooling calls).
2. The field shows up in the order detail (`get_order`) and in the customer
   order list (`list_orders_for_customer`).
3. The field is included in the daily billing export so the courier manifest
   that billing generates has it.

Nothing fancy: plain text, optional, empty by default.
