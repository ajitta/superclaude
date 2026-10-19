# payout

`split_cents(total, n)` splits an amount of cents into `n` shares for the
weekly partner payout.

Rules:

- The shares always add up to `total` — no cent is lost or created.
- Shares differ by at most one cent. The leftover cents go one each to the
  earliest shares, so `split_cents(100, 7)` is `[15, 15, 14, 14, 14, 14, 14]`.
