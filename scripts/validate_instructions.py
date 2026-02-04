#!/usr/bin/env python3
"""Validate INSTRUCTION_MAP coverage against TRIGGER_MAP.

Ensures every triggered file has a corresponding instruction entry,
measures token savings, and reports drift.

Usage:
    python scripts/validate_instructions.py
    python scripts/validate_instructions.py --verbose
"""

import argparse
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

CHARS_PER_TOKEN = 4


def get_maps():
    """Import and return TRIGGER_MAP files and INSTRUCTION_MAP."""
    from superclaude.scripts.context_loader import INSTRUCTION_MAP, TRIGGER_MAP

    trigger_files = {path for _, path, _ in TRIGGER_MAP}
    return trigger_files, INSTRUCTION_MAP


def estimate_tokens(text: str) -> int:
    return len(text) // CHARS_PER_TOKEN


def measure_file_tokens(base_path: Path, filename: str) -> int:
    """Measure tokens of a full .md file."""
    file_path = base_path / filename
    if file_path.exists():
        return estimate_tokens(file_path.read_text(encoding="utf-8"))
    return 0


def main():
    parser = argparse.ArgumentParser(description="Validate instruction coverage")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    trigger_files, instruction_map = get_maps()
    base_path = Path(__file__).parent.parent / "src" / "superclaude"

    # Coverage check
    missing = trigger_files - set(instruction_map.keys())
    extra = set(instruction_map.keys()) - trigger_files

    print("=== Instruction Coverage Validation ===\n")
    print(f"TRIGGER_MAP files:   {len(trigger_files)}")
    print(f"INSTRUCTION_MAP:     {len(instruction_map)}")

    if missing:
        print(f"\n!! MISSING instructions ({len(missing)}):")
        for f in sorted(missing):
            print(f"   - {f}")

    if extra:
        print(f"\nExtra instructions (no trigger): {len(extra)}")
        for f in sorted(extra):
            print(f"   - {f}")

    if not missing:
        print("\nCoverage: 100% - All triggered files have instructions.")

    # Token measurement
    print("\n=== Token Savings Analysis ===\n")
    total_full = 0
    total_instruction = 0

    rows = []
    for filename in sorted(trigger_files):
        full_tokens = measure_file_tokens(base_path, filename)
        instr = instruction_map.get(filename, "")
        instr_tokens = estimate_tokens(instr) if instr else full_tokens

        total_full += full_tokens
        total_instruction += instr_tokens

        savings_pct = (
            ((full_tokens - instr_tokens) / full_tokens * 100) if full_tokens else 0
        )
        rows.append((filename, full_tokens, instr_tokens, savings_pct))

    if args.verbose:
        print(f"{'File':<40} {'Full':>6} {'Instr':>6} {'Saved':>6}")
        print("-" * 62)
        for filename, full_t, instr_t, pct in rows:
            short = filename.split("/")[-1][:38]
            print(f"{short:<40} {full_t:>6} {instr_t:>6} {pct:>5.0f}%")
        print("-" * 62)

    savings = total_full - total_instruction
    pct = (savings / total_full * 100) if total_full else 0
    print(f"Total full file tokens:    {total_full:>6}")
    print(f"Total instruction tokens:  {total_instruction:>6}")
    print(f"Savings:                   {savings:>6} ({pct:.0f}%)")

    # Always-loaded chain measurement
    print("\n=== Always-Loaded Chain ===\n")
    core_files_old = [
        "core/FLAGS.md",
        "core/PRINCIPLES.md",
        "core/RULES.md",
        "modes/MODE_INDEX.md",
        "mcp/MCP_INDEX.md",
    ]
    core_files_new = ["core/FLAGS_COMPACT.md"]
    sc_core_estimate = 200  # inline <sc-core> block

    old_total = sum(measure_file_tokens(base_path, f) for f in core_files_old)
    new_total = (
        sum(measure_file_tokens(base_path, f) for f in core_files_new) + sc_core_estimate
    )

    print(f"Old chain (@5 files):      {old_total:>6} tokens")
    print(f"New chain (compact+core):  {new_total:>6} tokens")
    core_savings = old_total - new_total
    core_pct = (core_savings / old_total * 100) if old_total else 0
    print(f"Savings:                   {core_savings:>6} ({core_pct:.0f}%)")

    # Combined
    print("\n=== Combined Impact (Heavy Session: 5 flags) ===\n")
    dynamic_old = total_full * 5 // len(trigger_files) if trigger_files else 0
    dynamic_new = total_instruction * 5 // len(trigger_files) if trigger_files else 0

    combined_old = old_total + dynamic_old
    combined_new = new_total + dynamic_new
    combined_savings = combined_old - combined_new
    combined_pct = (combined_savings / combined_old * 100) if combined_old else 0

    print(f"Old (core + 5 dynamic):    {combined_old:>6} tokens")
    print(f"New (compact + 5 instr):   {combined_new:>6} tokens")
    print(f"Total savings:             {combined_savings:>6} ({combined_pct:.0f}%)")

    # Exit code
    if missing:
        print(f"\nFAIL: {len(missing)} files without instructions")
        return 1
    print("\nPASS: Full coverage")
    return 0


if __name__ == "__main__":
    sys.exit(main())
