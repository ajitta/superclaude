---
status: draft
revised: 2026-10-21
---

# Report export: design

## Components

- `report.py`: a new `--out <path>` option and a `--force` flag, parsed with `argparse`. `summarize()` stays as it is.
- `write_csv(summary, path, force)`: writes the header `count,total` and one row with the standard library `csv` module. It raises `FileExistsError` when `path` exists and `force` is false.

## Data flow

`main()` → `summarize(input)` → print the summary, or `write_csv()` when `--out` is given.

## Requirements coverage

| Requirement | Section |
|---|---|
| 1. `--out <path>` writes CSV | Components: `write_csv` |
| 2. No `--out`: unchanged | Data flow |
| 3. Overwrite only with `--force` | Components: `write_csv` |

## Areas of concern

none
