# Proposal: remove the retry wrapper from `client.charge()`

Owner: payments on-call
Status: needs a decision before Thursday's release

## Problem

Since the gateway migration, a declined card takes 3.5-4 s to come back to the
checkout page; p99 for declines was ~400 ms before. Support also reports that
the decline reason no longer shows up in our logs: we only see
`ChargeFailed: gave up after 3 attempts`, so agents cannot tell a stolen-card
block from insufficient funds, and they are escalating these as outages.

## Proposal

Delete `with_retry` in `client.py` and have `charge()` call
`gateway.post_charge` directly. The hosted gateway has its own HA/retry layer,
and the checkout worker already re-runs a task whenever the handler raises, so a
third retry loop on our side is redundant. Removing it takes declines back to a
single round trip and lets the real exception reach the logs.

## Rollout

One-line change in `client.py`, no config or schema changes. Can ship Thursday.
