#!/usr/bin/env python3
"""
Token Usage Comparison Script for SuperClaude

Compares token usage between two git commits to analyze the impact of
changes like the XML-embedded Markdown pattern.

Usage:
    python scripts/compare_token_usage.py [before_commit] [after_commit]

Examples:
    # Compare specific commits
    python scripts/compare_token_usage.py 3fe5300 ef54268

    # Compare HEAD~1 to HEAD (default)
    python scripts/compare_token_usage.py

    # Compare a tag to HEAD
    python scripts/compare_token_usage.py v4.1.8 HEAD

Requirements:
    pip install tiktoken
"""

import subprocess
import sys
from pathlib import Path
from collections import defaultdict

try:
    import tiktoken
    enc = tiktoken.get_encoding('cl100k_base')
except ImportError:
    print("Error: tiktoken not installed. Run: pip install tiktoken")
    sys.exit(1)


def count_tokens(text: str) -> int:
    """Count tokens using cl100k_base encoding (Claude-compatible)."""
    return len(enc.encode(text))


def get_file_at_commit(commit: str, path: str) -> str | None:
    """Retrieve file content at a specific git commit."""
    result = subprocess.run(
        ['git', 'show', f'{commit}:{path}'],
        capture_output=True, text=True
    )
    return result.stdout if result.returncode == 0 else None


def get_md_files(base_path: str = 'src/superclaude') -> list[Path]:
    """Get all markdown files excluding READMEs."""
    md_files = list(Path(base_path).rglob('*.md'))
    return [f for f in md_files if 'README' not in f.name]


def categorize_path(rel_path: str) -> str:
    """Extract category from file path."""
    parts = rel_path.split('/')
    if len(parts) >= 3:
        return parts[2]  # src/superclaude/CATEGORY/...
    return 'root'


def analyze_commits(before: str, after: str, base_path: str = 'src/superclaude'):
    """Analyze token usage difference between two commits."""
    md_files = get_md_files(base_path)

    # Category-level aggregation
    categories = defaultdict(lambda: {'before': 0, 'after': 0, 'files': 0})

    # Per-file details
    file_details = []

    for f in md_files:
        rel_path = str(f)
        cat = categorize_path(rel_path)

        before_content = get_file_at_commit(before, rel_path)
        after_content = get_file_at_commit(after, rel_path)

        before_tokens = count_tokens(before_content) if before_content else 0
        after_tokens = count_tokens(after_content) if after_content else 0
        delta = after_tokens - before_tokens

        categories[cat]['before'] += before_tokens
        categories[cat]['after'] += after_tokens
        categories[cat]['files'] += 1

        file_details.append({
            'path': rel_path,
            'category': cat,
            'before': before_tokens,
            'after': after_tokens,
            'delta': delta,
            'pct': (delta / before_tokens * 100) if before_tokens > 0 else (100 if after_tokens > 0 else 0)
        })

    return categories, file_details


def print_report(categories: dict, file_details: list, before: str, after: str):
    """Print formatted comparison report."""
    total_before = sum(c['before'] for c in categories.values())
    total_after = sum(c['after'] for c in categories.values())
    total_files = sum(c['files'] for c in categories.values())
    total_delta = total_after - total_before

    # Header
    print("=" * 70)
    print("TOKEN USAGE COMPARISON: SuperClaude Framework")
    print("=" * 70)
    print(f"Before: {before}")
    print(f"After:  {after}")
    print("-" * 70)

    # Category summary
    print(f"{'Category':<20} {'Files':>6} {'Before':>10} {'After':>10} {'Delta':>10} {'%':>8}")
    print("-" * 70)

    for cat in sorted(categories.keys()):
        data = categories[cat]
        delta = data['after'] - data['before']
        pct = (delta / data['before'] * 100) if data['before'] > 0 else (100 if data['after'] > 0 else 0)
        sign = '+' if delta >= 0 else ''
        print(f"{cat:<20} {data['files']:>6} {data['before']:>10,} {data['after']:>10,} {sign}{delta:>9,} {pct:>7.1f}%")

    print("-" * 70)
    pct_total = (total_delta / total_before * 100) if total_before > 0 else 0
    sign = '+' if total_delta >= 0 else ''
    print(f"{'TOTAL':<20} {total_files:>6} {total_before:>10,} {total_after:>10,} {sign}{total_delta:>9,} {pct_total:>7.1f}%")
    print("=" * 70)

    # Top changes
    file_details.sort(key=lambda x: abs(x['delta']), reverse=True)
    print("\nTOP 10 FILES BY TOKEN CHANGE:")
    print("-" * 60)
    for i, fd in enumerate(file_details[:10], 1):
        sign = '+' if fd['delta'] >= 0 else ''
        short_path = fd['path'].replace('src/superclaude/', '')
        print(f"{i:2}. {short_path:<40} {sign}{fd['delta']:>6} ({fd['pct']:>5.1f}%)")

    # New files
    new_files = [f for f in file_details if f['before'] == 0 and f['after'] > 0]
    if new_files:
        print(f"\nNEW FILES: {len(new_files)}")
        for nf in new_files:
            short_path = nf['path'].replace('src/superclaude/', '')
            print(f"   + {short_path}: {nf['after']:,} tokens")

    # Deleted files
    deleted_files = [f for f in file_details if f['before'] > 0 and f['after'] == 0]
    if deleted_files:
        print(f"\nDELETED FILES: {len(deleted_files)}")
        for df in deleted_files:
            short_path = df['path'].replace('src/superclaude/', '')
            print(f"   - {short_path}: {df['before']:,} tokens removed")

    # Context impact
    CLAUDE_CONTEXT = 200_000
    print("\nCONTEXT IMPACT:")
    print("-" * 60)
    print(f"Total context usage: {total_after:,} / {CLAUDE_CONTEXT:,} ({(total_after/CLAUDE_CONTEXT)*100:.1f}%)")
    print(f"Delta as % of context: {(total_delta/CLAUDE_CONTEXT)*100:.2f}%")
    print(f"Average tokens per file: {total_after // total_files if total_files else 0:,}")

    # Overhead estimate (for XML-embedded pattern)
    if total_delta > 0:
        avg_overhead = total_delta / total_files
        print(f"\nOVERHEAD ESTIMATE:")
        print(f"Average overhead per file: {avg_overhead:.1f} tokens")
        yaml_est = 60 * total_files
        xml_est = 25 * total_files
        print(f"  - YAML frontmatter (~60/file): ~{yaml_est:,} tokens")
        print(f"  - XML tags (~25/file): ~{xml_est:,} tokens")
        print(f"  - Content changes: ~{total_delta - yaml_est - xml_est:,} tokens")


def main():
    # Parse arguments
    if len(sys.argv) >= 3:
        before = sys.argv[1]
        after = sys.argv[2]
    elif len(sys.argv) == 2:
        before = sys.argv[1]
        after = 'HEAD'
    else:
        before = 'HEAD~1'
        after = 'HEAD'

    # Verify commits exist
    for commit in [before, after]:
        result = subprocess.run(
            ['git', 'rev-parse', '--verify', commit],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"Error: Invalid commit reference '{commit}'")
            sys.exit(1)

    # Run analysis
    categories, file_details = analyze_commits(before, after)
    print_report(categories, file_details, before, after)


if __name__ == '__main__':
    main()
