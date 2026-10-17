"""Checkout worker: pulls capture tasks off the queue and charges the card.

Delivery is at-least-once. If ``handle`` raises, the broker makes the task
visible again after the visibility timeout and it runs again, possibly on a
different worker instance.
"""
import client


def handle(task: dict) -> dict:
    receipt = client.charge(task["order_id"], task["amount_cents"])
    task["receipt_id"] = receipt["id"]
    return task
