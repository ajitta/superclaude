"""Remove duplicate CSV rows, keeping first appearance order."""

import sys


def dedup(lines):
    seen = set()
    out = []
    for line in lines:
        if line not in seen:
            seen.add(line)
            out.append(line)
    return out


if __name__ == "__main__":
    with open(sys.argv[1], encoding="utf-8") as fh:
        sys.stdout.writelines(dedup(fh.readlines()))
