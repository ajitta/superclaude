# ops-tools

Three small internal utilities that back the weekly operations run. Each
lives in its own directory, is owned by a different team, and has no imports
from the other two.

| Directory | Owner | What it does |
|---|---|---|
| `billing/` | Finance | Invoice line paging and totals for the statement PDF |
| `notify/` | On-call | Decides which alerts page the on-call engineer |
| `export/` | Data | Names and writes the per-team CSV drops |

## Running

Python 3 standard library only. From the repo root:

```
python check_all.py
```

prints one line per utility and exits non-zero if any of them misbehaves on
the reference inputs. Run it after any change to the three directories.

## Layout

```
billing/invoice.py   page_lines, line_total, statement_total
notify/alerts.py     should_escalate, route_alert, summarize
export/report.py     fmt_date, build_filename, write_csv
check_all.py         reference-input run for all three
ISSUES.md            open reports from the owning teams
```
