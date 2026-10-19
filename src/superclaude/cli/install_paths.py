"""
Path Resolution for superclaude Installation

Provides path constants and resolution functions used by all install modules.
Leaf dependency: imports no other cli module but the generated data table
``retired_skill_files``, so every install module can import it without a cycle.
superclaude.utils is allowed — it imports nothing from cli.
"""

import functools
import hashlib
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from superclaude import __version__
from superclaude.utils import detect_scope, same_dir, user_claude_dir

from .retired_skill_files import RETIRED_SKILL_FILES

# Component definitions: (source_subdir, target_subdir, description)
# Note: the hook registration is handled separately by install_hooks()
#
# Two target kinds. `commands/sc`, `superclaude/*`: superclaude-only directories,
# removed wholesale on uninstall. `agents`, `output-styles`, `skills`: Claude
# Code's own content directories, shared with the user's files, so install and
# uninstall touch only the names this release ships (SHARED_TARGET_COMPONENTS).
# `templates` and `skills` install one source subdirectory per unit
# (DIRECTORY_COMPONENTS); the others install files.
COMPONENTS = {
    "commands": ("commands", "commands/sc", "Slash commands"),
    "agents": ("agents", "agents", "Agent definitions"),
    "output-styles": ("output-styles", "output-styles", "Output styles"),
    "core": ("core", "superclaude/core", "Core framework (PRINCIPLES, FLAGS, RULES)"),
    "modes": ("modes", "superclaude/modes", "Behavioral modes"),
    "mcp": ("mcp", "superclaude/mcp", "MCP server documentation"),
    "templates": (
        "templates",
        "superclaude/templates",
        "Doc scaffold templates (consumed by /sc:init, not slash commands)",
    ),
    "skills": ("skills", "skills", "Skills (/sc-author, /sc-prompt)"),
}


# Components whose target directory Claude Code reads for the user's own files
# too. Uninstall removes only the shipped names there, and a local-scope install
# git-excludes them name by name, never the directory.
SHARED_TARGET_COMPONENTS = ("agents", "output-styles", "skills")

# Components that ship one subdirectory per unit and copy it whole. For these a
# shipped name is a directory name, not a .md filename.
DIRECTORY_COMPONENTS = ("templates", "skills")

# Files a directory component never installs, and drift never compares.
DIRECTORY_IGNORE = ("__pycache__", "*.pyc", ".DS_Store")


def md_names(directory: Path) -> set:
    """Filenames of the .md files in a directory, README excluded.

    A missing directory has none: Path.glob yields nothing for it.
    """
    return {f.name for f in directory.glob("*.md") if f.stem.upper() != "README"}


def shipped_md_names(component: str) -> set:
    """Filenames of the .md files a component ships, README excluded."""
    return md_names(_get_source_dir(component))


def dir_names(directory: Path) -> set:
    """Names of a directory's subdirectories, `_` and `.` prefixed ones excluded.

    A missing directory has none.
    """
    if not directory.exists():
        return set()
    return {
        d.name
        for d in directory.iterdir()
        if d.is_dir() and not d.name.startswith(("_", "."))
    }


def shipped_names(component: str) -> set:
    """The names a component installs: directories or .md filenames."""
    if component in DIRECTORY_COMPONENTS:
        return dir_names(_get_source_dir(component))
    return shipped_md_names(component)


def get_base_path(scope: str = "user") -> Path:
    """
    Get base installation path based on scope.

    Args:
        scope: "user" for ~/.claude/, "project" for ./.claude/ (team-shared
               content; the hook registration stays per-clone), or "local" for
               ./.claude/ (personal, gitignored)

    Returns:
        Path to base installation directory
    """
    if scope in ("project", "local"):
        return Path.cwd() / ".claude"
    else:  # user (default): $CLAUDE_CONFIG_DIR when set (ADR-0002)
        return user_claude_dir()


def find_install_root(start: Path) -> Path | None:
    """Nearest ancestor of ``start`` holding a project/local install, if any.

    $HOME is a candidate like any other. Skipping it — the first attempt at
    stopping a user-scope install from reading as a project one — made
    ``detect_scope``'s local-at-$HOME branch unreachable through the CLI, so the
    two disagreed for an install that is legal to create. Naming the scope is
    ``detect_scope``'s job and it now ranks $HOME correctly; this function only
    finds the directory.

    The walk stops at $HOME, inclusive. An install above the home directory is
    never the project's, and continuing past it made the answer depend on the
    machine: a start directory under the OS temp root (which Windows and a
    Claude Code session both place under the user profile) found the real
    user-scope install two levels up and reported it as a project one, even
    with ``Path.home`` pointed elsewhere. When ``start`` is not under $HOME the
    walk reaches the filesystem root as before.

    Args:
        start: Directory to search from, inclusive

    Returns:
        The directory containing ``.claude/superclaude``, or None
    """
    home = Path.home()
    for candidate in [start, *start.parents]:
        if (candidate / ".claude" / "superclaude").is_dir():
            return candidate
        if same_dir(candidate, home):
            break
    return None


def resolve_reporting_target(
    scope: str | None = None, start: Path | None = None
) -> tuple[str, Path]:
    """Scope and base path for the read-only commands: doctor, verify-drift.

    These walk up to the install, unlike ``get_base_path``, which deliberately
    anchors on the CWD because ``superclaude install`` writes where the user is
    standing. Reporting has no such constraint, and not walking up reproduced
    the failure this resolver exists to remove: run from ``src/``, every command
    reported a healthy local install as absent.

    An explicit --scope still decides the scope name; ``user`` always resolves
    to the home directory and never walks up.

    Args:
        scope: Scope the user asked for, or None to detect
        start: Directory to resolve from; defaults to the CWD

    Returns:
        Tuple of (scope name, base installation path)
    """
    if scope == "user":
        return "user", get_base_path("user")

    root = find_install_root(start or Path.cwd())
    if root is None:
        resolved = scope or "user"
        return resolved, get_base_path(resolved)
    return scope or detect_scope(root), root / ".claude"


def scope_command(command: str, scope: str, base_path: Path) -> str:
    """A command to print as advice, safe to follow verbatim from any directory.

    It carries ``--scope``: without it the command means user scope, and
    following verify-drift's bare ``install --force`` from a local project
    wrote a user install. Project and local scope write to the ``.claude`` of
    the directory the command runs from, so for them it also says where.

    Args:
        command: The subcommand and its flags, e.g. ``"install --force"``
        scope: Scope the command must act on
        base_path: That scope's .claude directory

    Returns:
        ``'superclaude <command> --scope <scope>'``, then ``from <dir>`` for
        project and local scope
    """
    quoted = f"'superclaude {command} --scope {scope}'"
    if scope == "user":
        return quoted
    return f"{quoted} from {base_path.parent}"


def has_install(base_path: Path) -> bool:
    """Whether ``base_path`` holds a superclaude install of any release.

    ``superclaude/`` marks every release since the fork; the v4.1.x pip CLI
    installed only ``commands/sc/`` (and a skill).
    """
    return (base_path / "superclaude").is_dir() or (
        base_path / "commands" / "sc"
    ).is_dir()


def installs_found(start: Path | None = None) -> List[Tuple[str, Path]]:
    """The installs a command run from ``start`` could have meant.

    The nearest project or local install at or above ``start``, then the user
    install. Each is ``(scope, base_path)``; the same directory is listed once.
    """
    found: List[Tuple[str, Path]] = []
    root = find_install_root(start or Path.cwd())
    if root is not None:
        found.append((detect_scope(root), root / ".claude"))
    user = get_base_path("user")
    if has_install(user) and not any(same_dir(base, user) for _, base in found):
        found.append(("user", user))
    return found


def found_installs_lines(command: str) -> List[str]:
    """One line per install ``installs_found`` names, with ``command`` for it."""
    return [
        f"   Found a {scope} install at {base}: "
        f"run {scope_command(command, scope, base)}"
        for scope, base in installs_found()
    ]


def config_dir_notices() -> List[str]:
    """What a user-scope command says about a CLAUDE_CONFIG_DIR away from ~/.claude.

    User scope follows the variable (ADR-0002), so with it set the install goes
    where Claude Code reads. Two things still need saying: an older install
    left in ~/.claude, which that Claude Code no longer reads (Q2 a: reported,
    never moved), and ``CLAUDE_CODE_SUBPROCESS_ENV_SCRUB``, which removes the
    variable from hook subprocesses, so the hooks look in ~/.claude (Q1 a).
    """
    if not os.environ.get("CLAUDE_CONFIG_DIR", "").strip():
        return []
    user_base = get_base_path("user")
    default = Path.home() / ".claude"
    if same_dir(user_base, default):
        return []
    notices: List[str] = []
    if has_install(default):
        notices.append(
            f"ℹ️  CLAUDE_CONFIG_DIR is set, so user scope is {user_base}. A user "
            f"install also exists at {default}, which this Claude Code does not "
            "read; to remove it, run 'superclaude uninstall --scope user' with "
            "CLAUDE_CONFIG_DIR unset."
        )
    scrub = os.environ.get("CLAUDE_CODE_SUBPROCESS_ENV_SCRUB", "").strip().lower()
    if scrub not in ("", "0", "false", "no", "off"):
        notices.append(
            "⚠️  CLAUDE_CODE_SUBPROCESS_ENV_SCRUB removes CLAUDE_CONFIG_DIR from "
            f"hook subprocesses, so superclaude's hooks look in {default}, not "
            f"{user_base}, and find no user install. Install at --scope project "
            "or --scope local inside a project, or turn the scrub off."
        )
    return notices


def _get_package_root() -> Path:
    """
    Get the package root directory.

    Returns:
        Path to superclaude package root (src/superclaude/ in dev, site-packages/superclaude/ when installed)
    """
    return Path(__file__).resolve().parent.parent


def _get_source_dir(component: str) -> Path:
    """
    Get source directory for a component.

    Args:
        component: Component name (a COMPONENTS key)

    Returns:
        Path to component source directory
    """
    package_root = _get_package_root()
    source_subdir = COMPONENTS[component][0]

    package_dir = package_root / source_subdir
    return package_dir


def _get_target_dir(component: str, base_path: Path) -> Path:
    """
    Get target directory for a component.

    Args:
        component: Component name
        base_path: Base installation path

    Returns:
        Path to target directory
    """
    target_subdir = COMPONENTS[component][1]
    return base_path / target_subdir


def _digests(text: str) -> Tuple[str, ...]:
    return tuple(text.split())


# Skills and agent files a release removed, each with the text of every
# revision superclaude shipped under that name: sha256 of the file with LF line
# endings (an agent's install-time `memory:` rewrite undone), first 16 hex
# digits, from the full history (tests/fixtures/shipped_names_history.json; a
# test fails when a name or a revision is missing). skills/ and agents/ are
# shared with the user's own files and with other collections (obra/superpowers
# uses ten of the skill names; `pm-agent` is a common agent name), so install
# and uninstall remove a file or directory under one of these names only when
# its text is one of these revisions. Anything else under the name stays.
#
# A skill's table covers every file it shipped (RETIRED_SKILL_FILES, generated
# into retired_skill_files.py); its SKILL.md decides whether the directory is
# superclaude's at all, and then only the files the table matches go.
#
# Without the install side of that prune, an upgrade leaves them in place: the
# auto-invocable skills (confidence-check, verbalized-sampling,
# using-superclaude) keep firing with no source left to explain them, and a
# local-scope install no longer git-excludes them, so they surface as untracked
# files in a team repo.
RETIRED_SKILL_DIGESTS = {
    name: files["SKILL.md"] for name, files in RETIRED_SKILL_FILES.items()
}
LEGACY_SKILL_NAMES = tuple(RETIRED_SKILL_DIGESTS)

RETIRED_AGENT_DIGESTS = {
    "deep-research-agent.md": _digests(
        """
        09869b8e4f9b2864 18267662f98cae9d 18a4a54e95be12a5 1ab5354faf368678
        1fad26d018dbf003 29768c28fd3ec088 30e0c1a04c05ac28 364dfeeae3d6325c
        37e562c0a9b65eb1 38efb390865eea53 3917c07d02cbe8a1 511166c4acd94b13
        512e867f7bc69882 531d8b8500a27da1 55be01776b133a15 5d5604f79c3f879a
        5f9bce5f9685f941 792d84e9ae954903 855b33d7fd1b44df 879608edb9d04e8a
        8d9dd01179439f80 90eacdee3c8d08cb 9dc6d6532365162e a5f7e80464dd80d4
        b48ad0765e4edf02 c10a866441f9bb79 c16d817e356d2c75 d533c74c50820374
        d574043ce4469d24 dd931b06f8ad33b2 de58ae7232b3855a ea596e1c754b2c06
        eb63f035017085e0
        """
    ),
    "deep-research.md": _digests(
        """
        1966ecf47e84d270 262002aacdca0942 31d09ec6f550050d 422c5f47d931af1a
        6354678e85ecff75 68d65a5dabad21cc 7218c1b062352783 76be9ca83fe4f6ca
        8009fb47730b20a2 822834affd172b2e 88226bc5466a7a5a 8a56ab180ca8e538
        8ed3526b0dff31a3 a2a38559c3dd866a a3b5508f0c357da7 d1634d46f831a345
        d466654d1e12c808 e28fbda94211ce47 f1cc3609fb00f1a7
        """
    ),
    "pm-agent.md": _digests(
        """
        0474919bc951eb8d 0b876558afde3764 0fe4f3e8ca4ba672 15744c9c9d7badd6
        16fb38b1f738fea6 1d49ab917ef125b6 276b465817827591 479ad358eb25dc17
        4f2355dfc9507c37 5848e5d949f2b544 609d5a99b9c57122 6b5a004782e1d564
        6df064bd80b88154 7dd96a39d49594d4 8f7bdf6598777ed7 8ff4b1442b047796
        904643b0129f3a10 918be78e1f6b27bd 9434b420c74b044f 959c436f6b70f025
        9c262f4c6acf9453 b1e57bc824a65ad5 b6854c410aa74fe1 be055540223440e9
        c46c79b86523fae1 c900e660b456406e d8b22d65d185e1d0 e12d0ede34b5ecff
        ea7165271c367428 ecba634c9d97c4b9 f1b91057416d51c8 f7482e5724cca723
        """
    ),
}
RETIRED_AGENT_FILES = tuple(RETIRED_AGENT_DIGESTS)


def find_unshipped(base_path: Path) -> list:
    """Installed files and directories this release no longer ships.

    Installing copies and deletes nothing, so an upgrade left a removed command
    running beside its successor (/sc:spawn, /sc:prompt) and the doc of a removed
    MCP server on disk. Only superclaude writes commands/sc and superclaude/ (uninstall
    removes both whole), so there anything the source does not ship is stale. In
    the shared directories only a retired agent holding superclaude's text is;
    legacy skills have their own helper. Non-.md files and superclaude/scripts/
    are never returned: a legacy hook registration may still run the script copies.
    """
    found: List[Path] = []
    for component in COMPONENTS:
        if component in SHARED_TARGET_COMPONENTS:
            continue
        target_dir = _get_target_dir(component, base_path)
        if component in DIRECTORY_COMPONENTS:
            found.extend(
                target_dir / name
                for name in sorted(dir_names(target_dir) - shipped_names(component))
            )
            continue
        dirs = [(target_dir, _get_source_dir(component))]
        if component == "core":
            dirs.append((target_dir / "rules", _get_source_dir(component) / "rules"))
        for target, source in dirs:
            found.extend(
                target / name for name in sorted(md_names(target) - md_names(source))
            )
    return found + find_retired_agents(base_path)


def find_retired_agents(base_path: Path) -> list:
    """Installed agent files a later release removed, holding superclaude's text."""
    agents_dir = _get_target_dir("agents", base_path)
    return [
        agents_dir / name
        for name in RETIRED_AGENT_FILES
        if (agents_dir / name).is_file() and _is_shipped_agent(agents_dir / name)
    ]


def find_legacy_skills(base_path: Path) -> list:
    """Installed skill directories left behind by a pre-removal release.

    Only the exact shipped names holding a shipped SKILL.md are matched:
    ``.claude/skills`` is shared with every other tool that installs skills, so
    anything else there is someone else's and must be left alone. A directory
    reached through a symlink (or junction) is the user's link, never followed.
    Once install has reduced one to files superclaude did not ship, it no longer
    matches: the user's now.
    """
    skills_dir = base_path / "skills"
    return [
        skills_dir / name
        for name in LEGACY_SKILL_NAMES
        if (skills_dir / name).is_dir()
        and not _is_link(skills_dir / name)
        and _is_shipped_skill(skills_dir / name)
    ]


def legacy_skill_files(skill_dir: Path) -> Tuple[List[Path], List[Path]]:
    """Split a retired skill directory into superclaude's files and the rest.

    A file is superclaude's when its path in the directory and its text are a
    revision that skill shipped (RETIRED_SKILL_FILES). Everything else is kept:
    a file the user added, a shipped file they edited, and every symlink —
    superclaude never shipped one, so one is neither followed nor removed.

    Returns:
        (superclaude's files, SKILL.md last so an interrupted removal leaves
        the directory recognisable to the next run; the entries kept)
    """
    shipped = RETIRED_SKILL_FILES.get(skill_dir.name, {})
    forms = _placeholder_forms(skill_dir)
    ours: List[Path] = []
    kept: List[Path] = []
    for path in _entries(skill_dir):
        rel = path.relative_to(skill_dir).as_posix()
        if rel in shipped and _is_shipped_skill_file(path, shipped[rel], forms):
            ours.append(path)
        else:
            kept.append(path)
    ours.sort(key=lambda p: p == skill_dir / "SKILL.md")
    return ours, kept


def remove_legacy_skill(skill_dir: Path) -> int:
    """Remove superclaude's files from a retired skill, then every directory
    left empty, deepest first. Returns how many entries were kept."""
    ours, kept = legacy_skill_files(skill_dir)
    for path in ours:
        path.unlink()
    _remove_empty_dirs(skill_dir)
    return len(kept)


def kept_skill_files_notice(skill_dir: Path, kept: int) -> str:
    """The line install and uninstall print for a retired skill that stays."""
    return (
        f"ℹ️  Kept {kept} file(s) in {skill_dir}: superclaude did not ship them "
        "(you added or edited them there); the skill's shipped files were removed"
    )


def _is_link(path: Path) -> bool:
    """A symlink, or on Windows a junction (Python 3.12+ can tell)."""
    isjunction = getattr(os.path, "isjunction", None)
    return path.is_symlink() or bool(isjunction and isjunction(path))


def _entries(directory: Path) -> List[Path]:
    """Every non-directory entry under ``directory``; links are entries, not followed."""
    found: List[Path] = []
    for child in sorted(directory.iterdir()):
        if child.is_dir() and not _is_link(child):
            found.extend(_entries(child))
        else:
            found.append(child)
    return found


def _remove_empty_dirs(directory: Path) -> None:
    for child in directory.iterdir():
        if child.is_dir() and not _is_link(child):
            _remove_empty_dirs(child)
    if not any(directory.iterdir()):
        directory.rmdir()


def _shipped_digest(data: bytes, digests: Tuple[str, ...]) -> bool:
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()[:16] in digests


def _placeholder_forms(skill_dir: Path) -> List[Tuple[bytes, bytes]]:
    """What ``{{SKILLS_PATH}}`` and ``{{SCRIPTS_PATH}}`` were resolved to.

    Releases cd2f8aab → b806c61c resolved them at install (in SKILL.md, the
    only file that carried them): the absolute path at user scope, and at
    local scope before 2026-03; the ``.claude/...`` relative path otherwise.
    The absolute path was ``str(...resolve())`` in the unreleased commits
    cd2f8aab → e1b2fbe7 (backslashes on Windows) and ``as_posix()`` from
    757e3649 (forward slashes everywhere), so both forms are undone. A copy is
    compared with each substitution undone too, in every file of the skill.
    """
    base = skill_dir.parent.parent
    forms = [
        (".claude/skills", ".claude/superclaude/scripts"),
        *(
            (form(root / "skills"), form(root / "superclaude" / "scripts"))
            for root in (base, base.resolve())
            for form in (Path.as_posix, str)
        ),
    ]
    return [(skills.encode(), scripts.encode()) for skills, scripts in forms]


def _is_shipped_skill_file(
    path: Path, digests: Tuple[str, ...], forms: List[Tuple[bytes, bytes]]
) -> bool:
    """Whether ``path`` is a regular file holding one of ``digests``' texts."""
    if _is_link(path) or not path.is_file():
        return False
    try:
        data = path.read_bytes().replace(b"\r\n", b"\n")
    except OSError:
        return False
    candidates = [data] + [
        data.replace(skills, b"{{SKILLS_PATH}}").replace(scripts, b"{{SCRIPTS_PATH}}")
        for skills, scripts in forms
    ]
    return any(_shipped_digest(text, digests) for text in candidates)


def _is_shipped_skill(skill_dir: Path) -> bool:
    """Whether a retired skill directory's SKILL.md is superclaude's text."""
    return _is_shipped_skill_file(
        skill_dir / "SKILL.md",
        RETIRED_SKILL_DIGESTS.get(skill_dir.name, ()),
        _placeholder_forms(skill_dir),
    )


def _is_shipped_agent(agent_file: Path) -> bool:
    """Whether a retired agent file holds superclaude's text (RETIRED_AGENT_DIGESTS).

    Install rewrites the first `memory: project` line to the scope
    (``install_components._rewrite_agent_memory_scope``), so a user or local
    copy is compared with that rewrite undone too.
    """
    try:
        data = agent_file.read_bytes().replace(b"\r\n", b"\n")
    except OSError:
        return False
    digests = RETIRED_AGENT_DIGESTS.get(agent_file.name, ())
    candidates = [data] + [
        data.replace(b"memory: " + scope + b"\n", b"memory: project\n", 1)
        for scope in (b"user", b"local")
    ]
    return any(_shipped_digest(text, digests) for text in candidates)


def _run(argv: List[str]) -> Optional[subprocess.CompletedProcess]:
    try:
        return subprocess.run(argv, capture_output=True, text=True, timeout=15)
    except (OSError, subprocess.TimeoutExpired):
        return None


@functools.lru_cache(maxsize=1)
def probe_console_script() -> Dict[str, Any]:
    """Where Claude Code's hook shell will find `superclaude`, and what it can do.

    Searches this process's PATH minus, when this interpreter is a virtual
    environment, its own bin directory. `uv run` (every `make sync-*` target)
    prepends the project venv, so a plain `shutil.which` found the venv's shim
    even when the user's shell — the one Claude Code inherits PATH from — had no
    `superclaude` at all, and the warning this feeds could never fire from the
    documented install path. A base interpreter's scripts directory is left in:
    `/usr/bin` after a system pip install, `C:\\PythonXY\\Scripts` from a
    python.org install, a conda base — those are the user's permanent PATH
    entries, and excluding them made a working layout read as broken. The
    script that is found is asked for `hook --help` (does it carry the
    subcommand at all?) and its version, because whichever `superclaude` PATH
    resolves is the package whose hooks run, not necessarily the one writing
    the registration.

    Cached: one probe per process; the answer cannot change mid-install.

    Returns:
        ``path``: the console script, or None. ``excluded``: the own-bin PATH
        entry that was left out, or None. ``has_hook``: whether it answers
        `hook --help` with exit 0 (None when nothing was found). ``version``:
        what its `--version` reports, or None.
    """
    in_virtualenv = sys.prefix != getattr(sys, "base_prefix", sys.prefix)
    own_bin = Path(sys.prefix) / ("Scripts" if os.name == "nt" else "bin")
    excluded = None
    search: List[str] = []
    for entry in os.environ.get("PATH", "").split(os.pathsep):
        if in_virtualenv and entry and same_dir(Path(entry), own_bin):
            excluded = entry
            continue
        search.append(entry)
    found = shutil.which("superclaude", path=os.pathsep.join(search))
    probe: Dict[str, Any] = {
        "path": found,
        "excluded": excluded,
        "has_hook": None,
        "version": None,
    }
    if found is None:
        return probe
    help_run = _run([found, "hook", "--help"])
    probe["has_hook"] = help_run is not None and help_run.returncode == 0
    version_run = _run([found, "--version"])
    match = re.search(r"version\s+(\S+)", version_run.stdout if version_run else "")
    probe["version"] = match.group(1) if match else None
    return probe


CONSOLE_SCRIPT_FIX = (
    "Put this release's console script on PATH ahead of any other "
    "(uv: `uv tool update-shell`; pipx: `pipx ensurepath`)"
)


def console_script_problems(probe: Dict[str, Any]) -> List[str]:
    """Why the probed `superclaude` cannot run this release's hooks, one line each.

    Empty when it can. The last line is the repair. One wording for `doctor`
    (a failed check's details) and `install` (one warning line), so the two
    never disagree about the same probe.
    """
    where = probe["path"]
    if where is None:
        lines = [
            "`superclaude` not found on PATH: every `superclaude hook <name>` "
            "registration exits 127 in Claude Code"
        ]
        if probe["excluded"]:
            lines.append(
                f"{probe['excluded']} was left out of the search — Claude Code's "
                "shell sees it only while that environment is active there"
            )
        return [*lines, CONSOLE_SCRIPT_FIX]
    if not probe["has_hook"]:
        return [
            f"{where} has no `hook` subcommand "
            f"({probe['version'] or 'unknown version'}): every hook exits 2 "
            "there, the blocking code",
            CONSOLE_SCRIPT_FIX,
        ]
    if probe["version"] and probe["version"] != __version__:
        return [
            f"{where} is version {probe['version']}; this install is "
            f"{__version__} — Claude Code runs that version's hooks",
            CONSOLE_SCRIPT_FIX,
        ]
    return []
