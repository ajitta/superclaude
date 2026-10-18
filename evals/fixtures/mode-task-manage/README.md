# tickets

A small command-line ticket tracker. Tickets live in a CSV file
(`tickets.csv` by default) and are managed through three commands.

```
python -m tickets.cli add "Fix login page"
python -m tickets.cli list
python -m tickets.cli close 1
```

Use `--file PATH` before the command to point at a different CSV file.

## Layout

| Path | Role |
|---|---|
| `tickets/models.py` | the `Ticket` record and its validation rules |
| `tickets/storage.py` | load/save tickets as CSV; `FIELDS` lists the columns the store knows |
| `tickets/cli.py` | argparse front end: `add`, `list`, `close` |
| `tests/` | unittest suite, one module per layer |

## Tests

Standard library only. From the project root:

```
python -m unittest discover -s tests -q
```
