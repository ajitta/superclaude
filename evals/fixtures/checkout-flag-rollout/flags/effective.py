"""Print the rollout each region actually gets for one flag.

    python flags/effective.py <env> <flag>
"""

import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent


def ceilings() -> dict[str, dict[str, int]]:
    merged: dict[str, dict[str, int]] = {}
    for path in sorted((HERE / "policy").glob("*.yaml")):
        for region, by_tag in (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).items():
            merged.setdefault(region, {}).update(by_tag or {})
    return merged


def main(env: str, name: str) -> None:
    flags = yaml.safe_load((HERE / f"{env}.yaml").read_text(encoding="utf-8"))["flags"]
    flag = flags[name]
    for region, by_tag in ceilings().items():
        caps = [by_tag[t] for t in flag.get("tags", []) if t in by_tag]
        print(f"{region:<6}{min([flag['rollout'], *caps])}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
