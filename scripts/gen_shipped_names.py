"""Generate tests/fixtures/shipped_names_history.json, the retirement guard's input.

    uv run python scripts/gen_shipped_names.py [<rev>]   # from a full clone

Every name and hook identity an install could hold, from every commit
reachable from ``<rev>`` (default HEAD), through both parents of a merge: a
pull's second parent was the public master, and a branch is installed by
whoever syncs from it. An unmerged branch is not reachable, so it never counts.
``tests/unit/test_install_upgrade_scenarios.py`` then requires every
identity not shipped now to be on a retired list in ``cli/install_paths.py``
or ``cli/install_settings.py``. Regenerate when a test there says the history
is stale (an agent, output style, skill or hook was added or removed). A
shallow clone is refused: it would drop the oldest names silently.

Collected:
  - every ``.md`` name under ``src/superclaude/agents/`` and
    ``output-styles/`` and every directory under ``src/superclaude/skills/``,
    with the first and last revision that had it, plus the working tree's;
  - for each agent and skill not shipped now, the sha256 of every revision of
    the agent file or SKILL.md (line endings normalised to LF), which install
    and uninstall compare before they remove a file or directory under that
    name: the name alone may be the user's own (``pm-agent``) or another skill
    collection's;
  - for each skill not shipped now, the same digests of every file of every
    revision, keyed by its path in the skill directory: install and uninstall
    remove only those files from a retired skill, so a file the user added or
    edited there stays. ``cli/retired_skill_files.py`` is written from this
    table (``render_retired_skill_files``), and a test holds the two equal;
  - every hook event and (event, entry point, subcommand) in every revision of
    ``hooks/hooks.json`` and ``hooks/serena-hooks.json``, and the commands with
    no entry point verbatim.
README files and ``_``/``.``-prefixed names are skipped, as the installer skips
them.
"""

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "tests" / "fixtures" / "shipped_names_history.json"
TABLE_OUT = REPO / "src" / "superclaude" / "cli" / "retired_skill_files.py"
DIRS = {
    "agents": "src/superclaude/agents",
    "output-styles": "src/superclaude/output-styles",
    "skills": "src/superclaude/skills",
}
HOOK_FILES = (
    "src/superclaude/hooks/hooks.json",
    "src/superclaude/hooks/serena-hooks.json",
)

# The entry point of a hook command, as cli/install_settings._hook_script_id
# reads it: `superclaude hook <name> [sub]` or `<interpreter> <dir>/<name>.py [sub]`.
CONSOLE = re.compile(
    r"(?:^|[\s/\\])superclaude(?:\.exe)?[\"']?\s+hook\s+([A-Za-z0-9_]+)(.*)$"
)
SCRIPT = re.compile(r"([A-Za-z0-9_]+)\.py(?=\s|$)(.*)$")
SUBCOMMAND = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_-]*")


def git(*args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(REPO), *args], capture_output=True, text=True, check=True
    ).stdout


def exists(rev: str, path: str) -> bool:
    return (
        subprocess.run(
            ["git", "-C", str(REPO), "cat-file", "-e", f"{rev}:{path}"],
            capture_output=True,
        ).returncode
        == 0
    )


def is_tree(rev: str, path: str) -> bool:
    out = subprocess.run(
        ["git", "-C", str(REPO), "cat-file", "-t", f"{rev}:{path}"],
        capture_output=True,
        text=True,
    )
    return out.stdout.strip() == "tree"


def touching(rev: str, path: str) -> list:
    """Revisions reachable from ``rev`` that changed ``path``, oldest first.

    ``--full-history`` walks every parent of a merge: path-limited history
    simplification would drop a side whose changes the merge did not keep.
    """
    log = git("log", "--full-history", "--reverse", "--format=@%h", rev, "--", path)
    return [line[1:] for line in log.splitlines() if line.startswith("@")]


def entry_point(command: str):
    match = CONSOLE.search(command) or SCRIPT.search(command)
    if not match:
        return None
    tokens = match.group(2).split()
    sub = tokens[0] if tokens and SUBCOMMAND.fullmatch(tokens[0]) else ""
    return match.group(1), sub


def digest(text: str) -> str:
    return hashlib.sha256(text.replace("\r\n", "\n").encode("utf-8")).hexdigest()


def is_shipped_entry(kind: str, name: str) -> bool:
    if name.startswith(("_", ".")):
        return False
    if kind == "skills":
        return True
    return name.endswith(".md") and Path(name).stem.upper() != "README"


def current_names(kind: str) -> list:
    root = REPO / DIRS[kind]
    if kind == "skills":
        return sorted(
            p.name
            for p in root.iterdir()
            if p.is_dir() and is_shipped_entry(kind, p.name)
        )
    return sorted(p.name for p in root.glob("*.md") if is_shipped_entry(kind, p.name))


def collect_names(rev: str) -> dict:
    names: dict = {kind: {} for kind in DIRS}
    for kind, path in DIRS.items():
        for commit in touching(rev, path):
            if not exists(commit, path):
                continue
            for entry in git("ls-tree", "--name-only", f"{commit}:{path}").split():
                if not is_shipped_entry(kind, entry):
                    continue
                if kind == "skills" and not is_tree(commit, f"{path}/{entry}"):
                    continue
                names[kind].setdefault(entry, [commit, commit])[1] = commit
        for name in current_names(kind):
            names[kind].setdefault(name, ["worktree", "worktree"])
    return names


def retired_digests(rev: str, kind: str, retired: list) -> dict:
    found: dict = {}
    for name in retired:
        path = f"{DIRS[kind]}/{name}"
        if kind == "skills":
            path += "/SKILL.md"
        for commit in touching(rev, path):
            if exists(commit, path):
                found.setdefault(name, set()).add(
                    digest(git("show", f"{commit}:{path}"))
                )
    return {name: sorted(values) for name, values in sorted(found.items())}


def retired_skill_files(rev: str, retired: list) -> dict:
    """{skill: {path in the skill dir: [sha256 of every revision]}}."""
    found: dict = {}
    for name in retired:
        path = f"{DIRS['skills']}/{name}"
        for commit in touching(rev, path):
            if not is_tree(commit, path):
                continue
            listing = git("ls-tree", "-r", "-z", f"{commit}:{path}")
            for entry in filter(None, listing.split("\0")):
                meta, rel = entry.split("\t", 1)
                if meta.split()[1] != "blob":
                    continue
                data = subprocess.run(
                    ["git", "-C", str(REPO), "cat-file", "blob", meta.split()[2]],
                    capture_output=True,
                    check=True,
                ).stdout
                found.setdefault(name, {}).setdefault(rel, set()).add(
                    hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()
                )
    return {
        name: {rel: sorted(values) for rel, values in sorted(files.items())}
        for name, files in sorted(found.items())
    }


def render_retired_skill_files(doc: dict) -> str:
    """Source of ``cli/retired_skill_files.py`` from the fixture's table."""
    lines = [
        '"""Every file of every revision of each retired skill (generated).',
        "",
        "Written by scripts/gen_shipped_names.py from",
        "tests/fixtures/shipped_names_history.json; regenerate, do not edit.",
        "{skill: {path in the skill directory: sha256 of each revision with LF",
        "line endings, first 16 hex digits}}, read by",
        "``install_paths.legacy_skill_files``.",
        '"""',
        "",
        "from typing import Dict, Tuple",
        "",
        "RETIRED_SKILL_FILES: Dict[str, Dict[str, Tuple[str, ...]]] = {",
    ]
    for name, files in doc["retired_skill_files"].items():
        lines.append(f"    {json.dumps(name)}: {{")
        for rel, digests in files.items():
            short = [json.dumps(d[:16]) for d in digests]
            if len(short) == 1:
                lines.append(f"        {json.dumps(rel)}: ({short[0]},),")
                continue
            lines.append(f"        {json.dumps(rel)}: (")
            lines.extend(f"            {d}," for d in short)
            lines.append("        ),")
        lines.append("    },")
    lines.append("}")
    return "\n".join(lines) + "\n"


def hook_rows(config: dict):
    """(event, command) for every inner hook in a parsed hooks file."""
    hooks = config.get("hooks") if isinstance(config, dict) else None
    for event, array in (hooks or {}).items():
        for entry in array if isinstance(array, list) else []:
            for hook in entry.get("hooks", []):
                yield event, hook.get("command", "")


def collect_hooks(rev: str):
    events: dict = {}
    ids: dict = {}
    inline: dict = {}
    for hook_file in HOOK_FILES:
        for commit in touching(rev, hook_file):
            if not exists(commit, hook_file):
                continue
            try:
                config = json.loads(git("show", f"{commit}:{hook_file}"))
            except json.JSONDecodeError:
                continue
            for event in (
                (config.get("hooks") or {}) if isinstance(config, dict) else {}
            ):
                events.setdefault(event, [commit, commit])[1] = commit
            for event, command in hook_rows(config):
                ep = entry_point(command)
                if ep:
                    key = (event, ep[0], ep[1])
                    ids.setdefault(key, [commit, commit])[1] = commit
                else:
                    inline.setdefault((event, command), [commit, commit])[1] = commit
    shipped = json.loads((REPO / HOOK_FILES[0]).read_text(encoding="utf-8"))
    now_events = set(shipped["hooks"])
    now_ids = set()
    for event, command in hook_rows(shipped):
        ep = entry_point(command)
        if ep:
            now_ids.add((event, ep[0], ep[1]))
    return events, ids, inline, now_events, now_ids


def main(rev: str = "HEAD") -> None:
    if git("rev-parse", "--is-shallow-repository").strip() != "false":
        raise SystemExit(
            "refusing: shallow clone (the history guard needs full history)"
        )
    head = git("rev-parse", "--short=8", rev).strip()
    names = collect_names(rev)
    current = {kind: set(current_names(kind)) for kind in DIRS}
    retired = {kind: sorted(set(names[kind]) - current[kind]) for kind in DIRS}
    events, ids, inline, now_events, now_ids = collect_hooks(rev)

    doc = {
        "generated_from": f"git log --full-history {rev} @ {head}",
        "generator": "scripts/gen_shipped_names.py (full clone only)",
        "names": {
            kind: [
                {
                    "name": n,
                    "first": v[0],
                    "last": v[1],
                    "shipped_now": n in current[kind],
                }
                for n, v in sorted(names[kind].items())
            ]
            for kind in DIRS
        },
        "retired_agent_digests": retired_digests(rev, "agents", retired["agents"]),
        "retired_skill_digests": retired_digests(rev, "skills", retired["skills"]),
        "retired_skill_files": retired_skill_files(rev, retired["skills"]),
        "hook_events": [
            {"event": e, "first": v[0], "last": v[1], "shipped_now": e in now_events}
            for e, v in sorted(events.items())
        ],
        "hook_ids": [
            {
                "event": k[0],
                "entry_point": k[1],
                "subcommand": k[2],
                "first": v[0],
                "last": v[1],
                "shipped_now": k in now_ids,
            }
            for k, v in sorted(ids.items())
        ],
        "inline_hook_commands": [
            {"event": k[0], "command": k[1], "first": v[0], "last": v[1]}
            for k, v in sorted(inline.items())
        ],
    }
    OUT.write_text(
        json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    TABLE_OUT.write_text(render_retired_skill_files(doc), encoding="utf-8")
    print(f"wrote {OUT.relative_to(REPO)} from {rev} @ {head}")
    print(f"wrote {TABLE_OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main(*sys.argv[1:2])
