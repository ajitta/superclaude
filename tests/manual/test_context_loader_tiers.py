"""
Manual test: compare Tier 0 / 1 / 2 injection behavior of context_loader.py.

Run: uv run python tests/manual/test_context_loader_tiers.py
"""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LOADER = REPO / "src" / "superclaude" / "scripts" / "context_loader.py"
CACHE_DIR = Path.home() / ".claude" / ".superclaude_hooks"


@dataclass
class Scenario:
    name: str
    prompt: str
    expected_tier: int
    expected_file: str
    note: str = ""


SCENARIOS: list[Scenario] = [
    Scenario(
        name="T0-context7",
        prompt="--c7 how do I use react query?",
        expected_tier=0,
        expected_file="mcp/MCP_Context7.md",
        note="Tool MCP → 1-line hint",
    ),
    Scenario(
        name="T0-sequential",
        prompt="--seq debug this multi-step issue",
        expected_tier=0,
        expected_file="mcp/MCP_Sequential.md",
        note="Tool MCP → 1-line hint",
    ),
    Scenario(
        name="T0-business-symbols",
        prompt="show me business symbol legend",
        expected_tier=0,
        expected_file="core/BUSINESS_SYMBOLS.md",
        note="Core reference → 1-line hint",
    ),
    Scenario(
        name="T1-serena",
        prompt="--serena rename this symbol across project",
        expected_tier=1,
        expected_file="mcp/MCP_Serena.md",
        note="Behavioral MCP → compact instruction",
    ),
    Scenario(
        name="T1-tavily",
        prompt="--tavily research recent AI news",
        expected_tier=1,
        expected_file="mcp/MCP_Tavily.md",
        note="Behavioral MCP → compact instruction",
    ),
    Scenario(
        name="T2-brainstorm-mode",
        prompt="--brainstorm let's explore ideas",
        expected_tier=2,
        expected_file="modes/MODE_Brainstorming.md",
        note="Mode file → full .md always",
    ),
    Scenario(
        name="T2-deep-research-mode",
        prompt="--research investigate this topic deeply",
        expected_tier=2,
        expected_file="modes/MODE_DeepResearch.md",
        note="Mode file → full .md always",
    ),
    Scenario(
        name="T2-verbose-override-c7",
        prompt="--c7 --verbose-context how to use react query",
        expected_tier=2,
        expected_file="mcp/MCP_Context7.md",
        note="--verbose-context overrides Tier 0 → full .md",
    ),
    Scenario(
        name="T2-verbose-override-serena",
        prompt="--serena --verbose-context refactor symbols",
        expected_tier=2,
        expected_file="mcp/MCP_Serena.md",
        note="--verbose-context overrides Tier 1 → full .md",
    ),
    Scenario(
        name="NO-TRIGGER",
        prompt="please write a hello world function in python",
        expected_tier=-1,
        expected_file="",
        note="No flags or triggers → no context loaded",
    ),
]


def clear_cache() -> None:
    """Remove session cache so each run starts fresh."""
    if CACHE_DIR.exists():
        for p in CACHE_DIR.glob("claude_context_*.txt"):
            try:
                p.unlink()
            except OSError:
                pass


def run_loader(prompt: str) -> tuple[str, int]:
    """Pipe prompt as UserPromptSubmit JSON to context_loader.py."""
    payload = json.dumps({"prompt": prompt})
    result = subprocess.run(
        [sys.executable, str(LOADER)],
        input=payload,
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=str(REPO),
    )
    return result.stdout, result.returncode


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def classify_output(out: str) -> str:
    has_hint = "<sc-context-hint" in out
    has_compact = "<sc-context " in out and "</sc-context>" in out
    has_full = "<context-inject " in out
    if has_full:
        return "Tier 2 (full .md)"
    if has_compact:
        return "Tier 1 (compact instruction)"
    if has_hint:
        return "Tier 0 (hint)"
    if "<sc-directive" in out:
        return "directive only (no tier load)"
    return "no context loaded"


def verify_verbose_warning() -> None:
    """Improvement #2: --verbose-context should emit warning before inflation."""
    clear_cache()
    out, _ = run_loader("--c7 --verbose-context library docs question")
    has_warn = "--verbose-context: forcing full .md injection" in out
    print("\n--- Improvement #2 verification: --verbose-context warning ---")
    print(f"  Warning emitted before inflation: {has_warn}")
    if has_warn:
        print("  ✅ Users see explicit token-cost notice before full .md load")
    else:
        print("  ⚠️  Warning missing — improvement #2 not effective")


def verify_missing_file_skip() -> None:
    """Improvement #3: TIER_0_MAP hint should be skipped if backing file is missing."""
    import os
    import tempfile

    clear_cache()
    fake_root = Path(tempfile.mkdtemp(prefix="sc_fake_"))
    (fake_root / "mcp").mkdir()
    # Intentionally do NOT create MCP_Context7.md — file should be reported missing.
    env = os.environ.copy()
    env["SUPERCLAUDE_PATH"] = str(fake_root)
    env["CLAUDE_SHOW_SKILLS"] = "0"  # silence skills summary for clean output
    payload = json.dumps({"prompt": "--c7 query"})
    result = subprocess.run(
        [sys.executable, str(LOADER)],
        input=payload,
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=str(REPO),
        env=env,
    )
    out = result.stdout
    has_skip_marker = "skip mcp/MCP_Context7.md: backing file not installed" in out
    has_hint = "<sc-context-hint" in out
    print("\n--- Improvement #3 verification: missing-file defensive skip ---")
    print(f"  Skip marker present:        {has_skip_marker}")
    print(f"  No misleading hint emitted: {not has_hint}")
    print(f"  Raw output: {out[:200]!r}")
    if has_skip_marker and not has_hint:
        print("  ✅ Phantom hints prevented when backing file absent")
    else:
        print("  ⚠️  Improvement #3 not effective")


def verify_session_dedup() -> None:
    """Improvement #4: skills summary should appear on 1st call, not 2nd in same session."""
    clear_cache()
    out1, _ = run_loader("--c7 first call")
    out2, _ = run_loader("--seq second call same session")
    has1 = "skills installed" in out1
    has2 = "skills installed" in out2
    delta = len(out1) - len(out2)
    print("\n--- Improvement #4 verification: session-dedup of skills summary ---")
    print(f"  1st call has skills banner: {has1}  (chars={len(out1)})")
    print(f"  2nd call has skills banner: {has2}  (chars={len(out2)})")
    print(f"  Token savings on 2nd call: ~{delta // 4} tokens")
    if has1 and not has2:
        print("  ✅ Skills summary cached after 1st emission")
    else:
        print("  ⚠️  Skills summary NOT deduplicated — improvement #4 not effective")


def verify_lifecycle_events() -> None:
    """Probe: cache behavior across /clear, /compact, SessionStart(startup) events."""
    RESET = Path.home() / ".claude" / "superclaude" / "scripts" / "context_reset.py"  # noqa: N806 — function-local constant path
    print("\n--- Lifecycle event probe: /clear, /compact, SessionStart=startup ---")

    def call_reset(source: str) -> str:
        result = subprocess.run(
            [sys.executable, str(RESET)],
            input=json.dumps({"source": source}),
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        return result.stdout.strip()

    def cache_exists() -> bool:
        return any(CACHE_DIR.glob("claude_context_*.txt"))

    def emit_count(prompt: str) -> tuple[int, int]:
        """Returns (chars, has_skills_banner) for first call."""
        out, _ = run_loader(prompt)
        return len(out), int("skills installed" in out)

    for source in ("clear", "compact", "startup", "resume"):
        clear_cache()
        # Prime the cache
        run_loader("--c7 prime cache")
        primed = cache_exists()
        # Trigger lifecycle event
        msg = call_reset(source)
        post_reset = cache_exists()
        # Re-issue the same prompt
        chars, banner = emit_count("--c7 prime cache")
        print(
            f"  source={source:<8}  primed={primed}  reset_msg={msg!r:<55}"
            f"  cache_after={post_reset}  re-emit chars={chars} banner={banner}"
        )
    """Probe: which outputs accumulate across N repeated calls in the same session?"""
    print("\n--- Accumulation probe: 5 repeated calls per pattern ---")
    patterns = [
        ("Tier 0  (--c7)", "--c7 lib question"),
        ("Tier 1  (--serena)", "--serena rename foo"),
        ("Tier 2  (--brainstorm)", "--brainstorm idea"),
        ("Directive (--loop)", "--loop iterate"),
        ("Notice (--no-mcp)", "--no-mcp run something"),
        ("Notice (--verbose-context)", "--c7 --verbose-context q"),
    ]
    for label, prompt in patterns:
        clear_cache()
        sizes = []
        body_signatures = []
        for i in range(5):
            out, _ = run_loader(prompt)
            # Strip the once-per-session skills banner so it doesn't mask other dedup
            body = "\n".join(
                line for line in out.splitlines() if "skills installed" not in line
            ).strip()
            sizes.append(len(body))
            body_signatures.append(body)
        unique = len(set(body_signatures))
        verdict = (
            "DEDUPED" if sizes[1] == 0 else ("ACCUMULATING" if sizes[1] > 0 else "?")
        )
        print(f"  {label:<32} sizes={sizes}  unique={unique}  → {verdict}")


def verify_serena_no_duplicate() -> None:
    """Improvement #1: --serena should no longer emit <sc-directive> (only Tier 1 sc-context)."""
    clear_cache()
    out, _ = run_loader("--serena rename function")
    has_directive = '<sc-directive flag="--serena">' in out
    has_context = (
        '<sc-context src="mcp\\MCP_Serena.md">' in out
        or '<sc-context src="mcp/MCP_Serena.md">' in out
    )
    print("\n--- Improvement #1 verification: Serena directive deduplication ---")
    print(f'  <sc-directive flag="--serena"> present: {has_directive}')
    print(f'  <sc-context src="mcp/MCP_Serena.md"> present: {has_context}')
    if not has_directive and has_context:
        print("  ✅ Directive removed; Tier 1 instruction retained")
    else:
        print("  ⚠️  Improvement #1 not fully effective")


def main() -> int:
    print(f"Loader: {LOADER}")
    print(f"Repo:   {REPO}\n")

    rows = []
    for sc in SCENARIOS:
        clear_cache()
        out, rc = run_loader(sc.prompt)
        size_chars = len(out)
        size_tokens = estimate_tokens(out)
        tier_label = classify_output(out)
        triggered = (
            sc.expected_file in out
            if sc.expected_file
            else (out.strip() == "" or "<sc-context" not in out)
        )

        rows.append(
            {
                "name": sc.name,
                "prompt": sc.prompt,
                "expected_tier": sc.expected_tier,
                "got_tier": tier_label,
                "chars": size_chars,
                "tokens_est": size_tokens,
                "triggered": triggered,
                "note": sc.note,
                "rc": rc,
                "preview": (
                    out[:300].replace("\n", " ⏎ ") + ("…" if len(out) > 300 else "")
                ),
            }
        )

    # Summary table
    print(
        f"{'Scenario':<28} {'Expected':<10} {'Got':<32} {'Chars':>7} {'~Tok':>6}  Note"
    )
    print("-" * 120)
    for r in rows:
        exp = f"T{r['expected_tier']}" if r["expected_tier"] >= 0 else "none"
        print(
            f"{r['name']:<28} {exp:<10} {r['got_tier']:<32} "
            f"{r['chars']:>7} {r['tokens_est']:>6}  {r['note']}"
        )

    print("\n--- Detailed previews ---")
    for r in rows:
        print(f"\n### {r['name']}  (rc={r['rc']})")
        print(f"prompt:  {r['prompt']!r}")
        print(f"preview: {r['preview']}")

    # Tier comparison sanity
    by_name = {r["name"]: r for r in rows}
    t0 = by_name["T0-context7"]["tokens_est"]
    t1 = by_name["T1-serena"]["tokens_est"]
    t2_mode = by_name["T2-brainstorm-mode"]["tokens_est"]
    t2_verbose_c7 = by_name["T2-verbose-override-c7"]["tokens_est"]

    print("\n--- Tier size relationship ---")
    print(f"  Tier 0 (--c7)         ≈ {t0} tokens")
    print(f"  Tier 1 (--serena)     ≈ {t1} tokens")
    print(f"  Tier 2 (--brainstorm) ≈ {t2_mode} tokens")
    print(f"  Tier 2 verbose --c7   ≈ {t2_verbose_c7} tokens  (was Tier 0)")
    print()
    if t0 < t1 < t2_mode and t2_verbose_c7 > t0:
        print(
            "✅ Expected ordering holds: T0 < T1 < T2 ; --verbose-context inflates T0 → T2"
        )
    else:
        print("⚠️  Ordering deviates from expectation — inspect previews above")

    # Improvement verifications
    verify_serena_no_duplicate()
    verify_session_dedup()
    verify_verbose_warning()
    verify_missing_file_skip()
    verify_lifecycle_events()

    return 0


if __name__ == "__main__":
    sys.exit(main())
