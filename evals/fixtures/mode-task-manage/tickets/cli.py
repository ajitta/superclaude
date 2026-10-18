"""Command-line front end: add, list, close."""

import argparse
import sys

from .models import Ticket
from .storage import load_tickets, next_id, save_tickets

DEFAULT_FILE = "tickets.csv"


def build_parser():
    parser = argparse.ArgumentParser(prog="tickets")
    parser.add_argument("--file", default=DEFAULT_FILE, help="CSV file to use")
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="create a ticket")
    add.add_argument("title")

    sub.add_parser("list", help="show all tickets")

    close = sub.add_parser("close", help="mark a ticket closed")
    close.add_argument("id", type=int)
    return parser


def format_ticket(ticket):
    return f"{ticket.id:>3}  {ticket.status:<6}  {ticket.title}"


def main(argv=None):
    args = build_parser().parse_args(argv)
    tickets = load_tickets(args.file)

    if args.command == "add":
        ticket = Ticket(id=next_id(tickets), title=args.title)
        tickets.append(ticket)
        save_tickets(args.file, tickets)
        print(f"created #{ticket.id}")
    elif args.command == "list":
        for ticket in tickets:
            print(format_ticket(ticket))
    elif args.command == "close":
        for ticket in tickets:
            if ticket.id == args.id:
                ticket.status = "closed"
                break
        else:
            print(f"no ticket #{args.id}", file=sys.stderr)
            return 1
        save_tickets(args.file, tickets)
        print(f"closed #{args.id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
