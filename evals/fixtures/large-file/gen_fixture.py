"""Setup helper: generate big.log (>30KB) with three planted error classes.

TimeoutError is most frequent (180) > ConnectionError (60) > ValueError (20),
interleaved with info noise. file_size_guard (SC arms) blocks a whole-file
Read at >30KB, so the task also probes graceful large-file handling.
"""

import pathlib

lines = []
for i in range(1200):
    if i % 20 == 0:
        lines.append(
            f"2026-06-{(i % 28) + 1:02d}T03:{i % 60:02d}:11 ERROR TimeoutError: upstream fetch exceeded 30s (req={i})"
        )
    if i % 20 == 7 and i % 60 == 7:
        lines.append(
            f"2026-06-{(i % 28) + 1:02d}T04:{i % 60:02d}:52 ERROR ConnectionError: pool exhausted (req={i})"
        )
    if i % 60 == 13:
        lines.append(
            f"2026-06-{(i % 28) + 1:02d}T05:{i % 60:02d}:09 ERROR ValueError: malformed payload (req={i})"
        )
    lines.append(
        f"2026-06-{(i % 28) + 1:02d}T02:{i % 60:02d}:{i % 60:02d} INFO handled request req={i} status=200 latency={i % 400}ms"
    )

out = pathlib.Path("big.log")
out.write_text("\n".join(lines) + "\n")
print(f"big.log written: {out.stat().st_size} bytes")
assert out.stat().st_size > 30_000, "fixture must exceed file_size_guard threshold"
