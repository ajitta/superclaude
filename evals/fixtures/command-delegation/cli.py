"""Tiny CLI used by the command-delegation probes."""

import argparse


def main(argv=None):
    parser = argparse.ArgumentParser(prog="tool")
    parser.add_argument("name")
    args = parser.parse_args(argv)
    print(f"hello {args.name}")


if __name__ == "__main__":
    main()
