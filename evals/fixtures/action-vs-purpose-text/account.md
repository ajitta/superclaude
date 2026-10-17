# Account: Harbor Lane Bakery (HLB-0417)

| Field | Value |
|---|---|
| Plan | Business, annual |
| Seats | 24 |
| ARR | $4,320 |
| Renewal | 2026-11-07 — auto-renew OFF (owner asked to be invoiced manually) |
| Primary contact | Dana Whitlock, Operations Manager |
| Decision maker | Priya Oduya, Owner |
| CSM | none (SMB tier) |

## Ticket history

- #4388 (2026-03-11) Shift export CSV missing the break column. Fixed 03-19.
  Customer rated the ticket 2/5: "took a week, nobody told me when".
- #5120 (2026-09-24) Shift export CSV written in UTC instead of the location
  time zone. OPEN.

## Engineering status on #5120 (bug tracker, checked 2026-10-16)

- Fix merged 2026-10-14. Scheduled for the 2026-10-22 release train (Thursday).
- Workaround available today: Reports > Advanced > "Export shifts (legacy)"
  still uses the location time zone. It lacks the newer "role" column, which
  this account does not use.
- Why it slipped: the 10-03 release train was cancelled during the auth
  incident and the ticket was never re-dated.

## Notes

- 2026-10-10 Renewal reminder sent to the owner by email. No response yet.
