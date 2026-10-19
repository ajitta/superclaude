"""Copy static assets to content-hashed names and write web/static/assets.json."""

import hashlib
import json
import shutil
from pathlib import Path

STATIC = Path(__file__).resolve().parents[1] / "static"
PATTERNS = ("*.css", "*.js")


def main() -> None:
    manifest = {}
    for pattern in PATTERNS:
        for path in sorted(STATIC.rglob(pattern)):
            if path.stem.count(".") or path.name == "assets.json":
                continue
            digest = hashlib.sha256(path.read_bytes()).hexdigest()[:8]
            target = path.with_name(f"{path.stem}.{digest}{path.suffix}")
            shutil.copyfile(path, target)
            manifest[path.relative_to(STATIC).as_posix()] = target.relative_to(STATIC).as_posix()
    (STATIC / "assets.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
