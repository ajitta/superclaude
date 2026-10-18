# Open reports

## Finance (billing/)

The statement PDF is missing the first ten lines of every invoice. An invoice
with 25 lines prints lines 11-20 on page 1, lines 21-25 on page 2, and page 3
is blank. Totals at the bottom are correct, so the lines are being counted —
they just never show up on a page.

## On-call (notify/)

Alerts that land exactly on the configured severity threshold are never
paged. Our threshold is 3 ("high"). Severity-4 alerts page fine, severity-2
alerts stay in the log as expected, but every severity-3 alert this week was
logged and nobody was paged. The runbook says "at or above the threshold
pages".

## Data (export/)

The CSV drop for 7 March was written as `ops-2026-07-03.csv` and the one for
12 January came out as `ops-2026-12-01.csv`. The files themselves are fine;
only the name is wrong. Drops where the day and month happen to be equal
(e.g. 5 May) are named correctly.
