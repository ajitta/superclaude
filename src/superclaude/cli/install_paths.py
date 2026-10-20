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
    "backend-architect.md": _digests(
        """
        01c6e34f976b6d02 056b6b68f5ce30e6 0c2423c7038b9363 0df0b5a28ff94f3f
        0ee89d048b28cb65 17e417cac0735af0 19e9ad671014f05c 1f012f3a101c6a98
        209e57358058d9ea 23df3e884971ae87 24fa82d3b2d27a20 25805dbc1664ec3e
        263a801cea7f8277 2743009c45b35108 30f14d5275e0cd2a 31de5d52c7a46752
        3d05e4550642681f 3e363bcd5aa686c9 45dfb25c44344fd1 4600e385bcb3caa8
        476832e486df7197 48196ffbb863f7b9 4a6d955edcd04a5e 4b7a37de4169debe
        4ba7bfda66c73055 4e73ff9fdf55cf07 508e180083b3491c 59a94ad1d6181268
        5cb55295a35800ae 5f576191248327d2 64e5f48bec0f88dd 6959a67a1aea423b
        6a507b337fea79b3 75e57edcea116e02 79f085b25029c2f9 7cfce5969fdcb986
        83ac83414d51f8dd 84618e12161340ed 86bc6824d162907d 89038be99d0910b6
        9422c4a7350bd725 aac3b8f0e1f2ef6d b230114d23eb3a62 b40d9a15fcc2ef96
        b9b9d7888c76ea9b c15f708f27746984 c18d4d109fb6f353 c2b5fdf3c21d9fe6
        c47f4e19a7c56573 c61c5ed0c2e0bfa6 c9d21c93411d7ca0 ca33333c24fb4930
        cc47075cbf207241 d0d0f2c72741df89 d0e46f6aed65336e dd9f75c5f1add076
        de80b680e9a10f82 ebb1518798f0c165 ebffb4c7f35b29d7 ec1ffef47457c80b
        ef03dadf70d56bf0 ef591660808f70ea f74021be2ad8fc57 f9285635e145610e
        """
    ),
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
    "devops-architect.md": _digests(
        """
        0cae08442afe7288 0ce1ff777d3fb617 0db3d7c49a029cd4 137229f850364178
        14aa4c3cb7163a43 19e7d39d1e2d6245 1d4ce0ad8fbe80c3 1fa57487900c1307
        2296274a689e9a9b 29b4f3a65100b335 2a071c459920add9 2aed0a81b49cabfd
        38899f0286a42881 4052ba31285b3974 42d4cb159c2c9123 483c92d6511eb1b5
        4f92eaed1a1e5dae 56d64ac6786670ac 5c3c1de472339333 60b8de56716c78cc
        62c8400f005c8143 655eec7858e5aca6 65be14df1b2ad57a 67b3c89b88d2cc14
        68673a0d5ae6ad2f 7531b7809a439242 78404db05886063c 7891eabc7a6377b4
        79fc0be3b9691740 7e2c8205f9e59986 7f1064d9e7d48f99 83e35806d81e6d9b
        96b1e385783f7dc1 98eda9f7f2277fd1 9c309559c9164856 a1fa892f04ecbf67
        a471da3ca30e0ddd a7ddaa9f9811aff4 abb658244093a92a b1285378e10d149f
        c293e343c8274848 cc18a84495123671 d35086b2d998d495 d3fc5a0a9604d3e2
        d4e1f632694048f9 e2482a28320456de e96c44e3a50d3329 e9c37b5a3c96b305
        e9d1ab73c9f55aa4 ea6a4ec329957163 fb36902e25e4b7bd ff98214c0b4af953
        """
    ),
    "frontend-architect.md": _digests(
        """
        0313fe4190c95dd1 040dc741d4b4e6d2 0475de1fea148a94 0590d9f4f73c1286
        064d234814321a5b 0d91cd154c45ded3 0ec322cb417a8ef5 102456cc318b15f9
        103e01235bc111ab 118fdf54311b003e 15a75e3b90b9d6fd 179166f243ee09fc
        1f70350a43d4e989 2639008a74f972a4 2842d7b5999b8826 29610b783abee7fc
        2d1b63c76adfc224 2d233332d4a6d02a 307a035a6111b9d2 354b19d9bacbb0be
        377bc91a21ec4465 389fce79e3ec8e9a 3f63028a17a1f10b 416acf4acc3975f5
        419524891af41d12 4dc7bcb7f6d52faf 5174a0ab1f4cd661 55c167d7e9ce6bb1
        5afe795d0708fdbf 5cbf5fa555ced5ec 6090b87f2b8fb136 624761aeb0536a01
        66b0ca9701c02a76 66dea0caa7f51b18 79396e40139a3d3e 7aee1a87980e712b
        7b6016039492cf15 81a224c33c37f7a3 82a033a43a48e34e 846e8dd4c0f55fa2
        84bf1745b2e56cc6 88515cdd8503fc0a 8ab77c17d8765858 94f382bc68cff7b6
        97829e91fbb82052 9d0fbf0ec1c88262 9d22365cf8b9967b aa6ffbdeddd152fa
        ab577bcdc5e0631d ad31ea02e0a82960 adb1f86ea30afc40 ae450840bd171b8c
        b5073895891a3433 c25a44d63017b110 c99879582cefc0c2 cd6c70e31d7f7e1d
        cfcc6273a9e94829 d03c2ace952847bf d1299e0671e35a10 d6acdb7df8501a47
        d8a45e5e54133a13 d9a86eb01837a410 ddf0df25b12e58c8 e0bd47d526778c1e
        e3efb9d3d63d749e e59df2abfea95b32 e854bbbc6ca3f19f e9d27c3f9f8f05f8
        eb8880d43bd53ca4 edd438dfcfa80f8e f6eca257a006b17e f7e48be97cc96c4e
        f93d743b0d79f3f9 fc2631e857b44994 feec22c5f98e9ce1
        """
    ),
    "git-workflow.md": _digests(
        """
        04c8cb5a337407cc 06aabc5e5d2921a7 09c52bed08d37272 0fadeafcc1313ce5
        150fedcad08071dd 208e95aa3b75103e 22be5eaf9b826c19 245c55dfb7a0dbc0
        265fe743e45ad882 2b8c0da986b460e7 368c86caae69153c 4327e9030616d10e
        4ad7ed5b5c1b7b68 537a1cb3800d6d1f 62a0f72c933eaaea 6902698faf3bab59
        6b0c300948273097 71e103184c0a4334 7715c27d4d9eebd3 7eda07cc846f6f73
        818812e04656b159 86cfa35ce099d0da 90d4ef29769e4448 98fd49892cbb2db5
        a26448a18669fcc7 a8329c528127598e c2d3d1665f62df0b c55692ebc0af8ced
        c8f5ddbdaad8e87b ca070ae35f7741aa cc31d9af2f114a6a cd044778df15761b
        d3cec78850d20833 f08f2f982b13420c f3c4be4556296208 f87ef8f4870ef6f3
        f8a94095bc9e4758 fe059d00f686d0b8
        """
    ),
    "insight-analyst.md": _digests(
        """
        06b23d94cb694bd5 1884053f1eff6432 309d0940f477b603 311f1c94436d3bec
        3744c272434d4c89 376f0d064ede7b1b 3eb7229726f5b06a 4269dd7856f1c5e4
        794fd7207af40b9a 7a1841e104950bca 7c115b9873d27517 7e2e6d651b99a705
        81bafdd75a752163 9a7cf4b2e36e8bf3 9c7afbcde928f1ca ae8f2f52120d66e7
        e154c5d1451411a3 e1a1180acf60ac3c e843f3899e3006ba
        """
    ),
    "learning-guide.md": _digests(
        """
        036c7da9dbe4a75e 0cd9e9c85121ef6f 0e71988b8c9b1068 0ff60624d03049d0
        10ca5005e1013841 11c50434f95a7a36 171ae22b7459c6ea 1b2ae742a6711331
        2326f08cbb7ac7fa 29c431c623ed5f53 2a08773f82471e59 2dce33f750dac0c3
        2e7916b9a78d9b68 3454f53d5ee3440f 3509a33968f7875b 38f49a87be6c0b97
        39358e07da0cc1c0 39531e471e8e8013 4d5c2101504dab77 4f2454fd02fd0119
        54558f338c1aece2 5bb4c77f707f8879 63b2a998c7b65c6f 640457f90cfebdb9
        6a03cb5205c49002 6a9d8c91bd752048 6c97888c32b57915 6e83fa69c52e1939
        8e23772ae1d79bc7 8f6bb3f62bb91598 9153114be63f71b3 98d68ac78339e456
        a144862d4c2ac3a6 a6a45020dd922d5c a7396173a33740c1 a7a4b956c0d6e226
        aa53bed8ff260898 afe447ab23c7fe47 b7f8b9ac4c2f4f14 b7f99411ac33bbe5
        b8ce296625ff23df ba97e6ac5421f030 bd57b88ea71d47db be5a47fec7d8cadc
        c12a3a5b793e30c0 cfb75a842cec4468 d09ea120ddebc55c d45310ddfede0f60
        d9fd485f3875541f e85623d609d7c1a4 e96cf8b145f7f287 f1612f98ad759598
        f415e1e8a7ddad2d f553412ec45ff9e8 f6ac63987455fc54 f6fe5ecf60751a8c
        f75048f5aee1a516 f78307af5893fe44
        """
    ),
    "performance-engineer.md": _digests(
        """
        03f4c2ea2f91bed0 06d7dc5859c2fd4b 0a320bf695dc68e5 0d5a35c8edb950ae
        0e6ed09329c7df18 11d9554084ef2026 14b0704cc0657ace 1b9ff131602574eb
        1f6f628f8f20455c 202a77a8f1b7920d 2128f45810d3b13d 21911d7385d3779a
        21a338208c6a036c 223081a833b892af 223e6de6bca9a6b8 2a675f6a4d7c6569
        30fff68f8c53bab1 341fcbd37147b538 3871dc039fb86e12 3c936616cc222f4e
        450d0b62a57d2d2a 4d491de8044dfc54 4f68716cf561bc9f 52885dbd55d7f92a
        57e9c69a2504677b 58d9927c9f6e13ae 62b06bd922be2a2b 636520943893a0ed
        7c042198cb2e2710 7f99f1aa77d30f77 8d4b7eeafc64620d 9381734be12b21ad
        96a6a4822267fc31 ab4824463fa8e174 aeaaa8f6d7a659b6 b197861d4bb7facc
        ba0f345407a2d6da bd5aff6c7542c28a be207dac4a76d114 bf7d4a158c0545ec
        c5d7de3cf4e86398 c619f50d9e774c92 c81c61bb3522d2aa cc1a69c54f693179
        cc393d433e2bb91d ccedb42f7ad7c42c d1758473c8b1f77d d4624ddf185ce3bb
        d610ffad17a220e0 d6c3e48ef34e68e0 d96c2af4338e6fa3 e18d2bda1b597ee3
        e24aed4114cda540 e702b19251556f00 e73e0bf5eb6b863e edddd155352c22b0
        ee1b5854d95fafa5 f99023fd155e8752 fbdb20ff1812399b
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
    "project-initializer.md": _digests(
        """
        015975a3a5534523 03d5ac5c5a781730 094eb81a756507a4 17291e84b9cf4ed5
        178a4bde6debd09d 1e8fd71b7d8dd0ee 1eb115b21f4fc090 202f03a39728e299
        304af880f98e7954 407f28c38008f398 45cf1c39df36094b 50db7bc13b9a77a8
        5894874e3ec04b7c 5c081f2bc110e396 5f46d7b904a4c68d 6ba5dfa3fa0c34e4
        6f372304cd35ef87 82791359f9ba2fd0 82849ab169a8df85 82f2d4748d210119
        8672601543faab71 99b46d19abeefe47 99c940878b0dfa09 99db5d5b27c3e8fd
        ab1158466c2c00ae ac7b782c45ebe08c b66f5d47a3a4e1f7 b822c0640b5acfad
        ba87edf4e3c86c74 c5ed99ecbf4a960d cf9df44f5b5419fd d23322c1de71c5b6
        d8b71f05ecfec099 dd9165a5e98ce372 e05ac906f34f693d e1ce2a42c28af868
        f0f104b244fe936c f2629f0848a7a0ba fded5d7a83a98c0d
        """
    ),
    "project-manager.md": _digests(
        """
        00308aeed2e915fb 02c7fd2b0497aad6 03ef98bef9da893d 07b77171f2fe66c6
        0dbe1ac81bb02b9e 0e806d7c4b419d25 1b2837271770d8a9 1ca12cbc5c6b13d3
        218279530acfed47 339c8283fcf21723 37928933cf796628 3e5873ec453a44ac
        44eb5c9a70aae81c 4580c3313d8e7428 4c0e3d40afe1b834 4fc3ddd1fafa562d
        5420ee9838e2c8fd 581f40dd1db1d7ae 6292c0e5adda2040 6ab687935863d33f
        7aa9740b266c0814 7b456852dc9f6bed 8b68c992165e6f8e 98bb00ac823517b0
        b2f849ed7705d5a2 bf03316c7f7e7698 bfb604d69b9357e7 c028b1130811afa7
        c8ce4bbee128b090 d2af2fb3b7afe920 df54f2173d86b03f e607bcca9c5f49f2
        ea60ad739e863b5d ebd1f8c88b4593cc eeda6475a91a5655 f0c4085035252b08
        fb216feb4bc03977
        """
    ),
    "python-expert.md": _digests(
        """
        0449792ef23d8a8c 05e5f3c731ac10a0 09b10d29898c7609 0b324d53cd11c1d4
        0cec24b3fe7c5906 17ba2afc6a500039 17e9aa38c593be12 18c7e092b147c582
        1945d19fe42b1d86 1d4f888e38ee670a 1f91b1c09260c91a 261445c4ab99c11f
        276c5b81b7d0fe72 28ab07494e52f91b 28fedeb2e97600d3 2a5fc5e7844a1ba4
        2b07abcd9f7edd6e 2c37374d310d85b9 2d76a18d378ad9fe 339430f8457bc4ce
        493a3119026f514b 4bc682a1cd313117 510b022f994b793b 511f0dbf84cbb41a
        55efb47a7241e05c 619fca276f9118a1 62b3d2c1f27e216b 62d2be718396441e
        711da0411789677d 7ea15cd0a4f9a576 8f1b9b083d4b24f8 8f3df3d7071ec580
        92045d85011d2d4e 92aeadd7ed8fad5f 93eedb640ba3f37d 9507c958e5140edc
        9f2c430463cd48dd a4747f42c5d0d994 b24e6675948c0b91 b3cdf84f5e64d130
        b6c67c103bf5b0e0 bda329c8b90a3261 c162a4565f1d4b57 c5a4172b16b49740
        c606b0caee22d164 cf56a25a51cff930 d04ec1444ec63968 d37f237c4d258fad
        d63720f03e11101d e05fb3f76a4bae28 e0810b0320c00a38 e20266aba7ead93d
        e83ff4dba91e0192 ecff0899735d936c ef17bae0271abe50 f1cbe1b8bbf0d2be
        f3ecc50721e8bf1d f6994ff9e40d1fb3 f6bcf985bf9f1019 f823ff35d39f3324
        """
    ),
    "quality-engineer.md": _digests(
        """
        03e484dbfbbbb204 083faf248fcf4547 092e809fcda27c40 0d821db20aad2cf2
        114e1510b44d3530 166389238a4b03b4 17c5e20c9e80b651 1861354526a26d1e
        2739f7115b9ac973 30103595a7374da6 30a2a6ee156acc92 36c5c1e86e20a6f2
        3d640f1f200802e3 40532a0f7713d799 549c193c4f22a4e8 55c557b40d49c80b
        563451915656d37f 570b712ab8215494 59ac07c8fec34719 65a961e7aa50ecee
        7829c20063c5fca0 786101a05b2c544f 794d056e2bf533a9 8101dde43d46ea39
        8956d271e013bc9c 8bd99bdf73def421 8e55cd744122153d 8eb2c2070279066c
        93f4bbba6f6d5349 95c82208dca012e9 97c73229832bf9e1 99ade7d54f548321
        9c5dd3ec9a616b02 9e064a55d6c5b698 a53245acf9e86454 a616bd70adf0da9d
        a66d38300caf3392 aa5f3bdb8382a540 ab3fd2538aab8b88 abb8e767bf2bc677
        b189045a7d5747af b2e877e299c6e373 b50376509b40e751 b584438a4bd94680
        b9356512c29402ac bbaa9a5ff7e3d162 c73af473790a2330 cb2342fd3186f96f
        d24deeafaec77b16 d2b6f4065430926a d3989c940a45bd2a d63fdfd7f1b44b55
        d8987d46bcbacc9c d8b916d645406609 e5a9b72e6c25ff0b eaabd6993c5227fe
        eb21f66f040771a5 f104c3c80a38041a f28ed5b28a305a0b
        """
    ),
    "refactoring-expert.md": _digests(
        """
        019321c06eaf229d 038ac4afce393d51 066f5df34e12eae6 07d1c53a405a5bad
        0f854aa14a9c3f8f 156b847ab5fbe479 19e238452ccec01e 24075d90ee38c1cf
        2409468114c2d546 244774bf77489db2 3366ba52510e3158 3952eae6ce2572b6
        3bf1cee23599cd6d 3c61cf68d6ad0f68 49108b48b73a6dfe 4a92d75abe4cbc7a
        5b20b2a57d2e6416 5bf210c85a2aeeb0 5e7cba62fc5fce14 6077a6d43acef666
        6432995e3d6a04ed 6ceeedf386fead3c 6fd9666e3d0d83a6 7854abab618da250
        7bf83be045933121 7e9f3fd3a1767486 80c4a0cce8b74111 81560a165a49b7cc
        836ce670361250fc 93341bb31ab9af7c 93b89240d03bd807 97116087fa31e713
        9bf724f2ca84e4d9 9fa9e7422cef4be7 a55cf424246664e6 a59327e524d0e527
        a604ba87ac6ffe1e a9e1dd7eac70e942 aa3885d6ad78599b b2e83b51fc6cd559
        be16efff27db8078 c5364a77a55501d8 ca40b048a7eb7661 cb91caf171ea81ed
        cbb988a9fa29e0c6 cd71b34cb5b13b8e d07c6f0a073456e6 d1d3bcbb933eda32
        d77cdbeae6b1f783 db4f0d6ac0a81e7e e0be48c39678d14d e24b87111af3278a
        e4f0eb0e92a656eb e72709357e8a37f8 f245280ff774f523 f85a77707affb41e
        f99ecacf9d27a603 ff4fb4238a4459b9
        """
    ),
    "requirements-analyst.md": _digests(
        """
        011a4e7a27fec6dc 0362202339e29742 0884ca21e06555bf 090f8488789e14a3
        09b798594613918a 0b092de1c9253f77 0ca4e1d8d1a5bc03 128124fda137518d
        1320ad47c9b28e84 1d90e1227f0f6868 1e6e984f105821cd 1f85e8eb5c24de84
        29545a5019bbdf14 2e3a40414e15d61d 38bd6e78b12d64b2 3b386cf211fd5457
        438e275bb6161115 44945fb513888e91 457f3e41f136167a 46a9469019aafbd2
        4e2d461159b33b9f 54ca25d59361c5ed 5b777769f62797f9 633ee82b72ea364e
        6594c4ed5d137caa 68afee218c24bb30 691f6ed95d5305e8 696ef1da2837d864
        6ff598eeeb6c4df9 703f1cb9e1152f3a 833f79cc28b3c84b 852263071f116ba7
        86bdb49cf6d46cb5 8cceead7fea937de 99447295e8448db3 a148ddb6ef4199c6
        a34564aa3701ed65 a3a1363166444f5b a6dea0f773b0e1d6 a7dfe3fc6a07c36e
        a99353133b2baa1f ab7ee32481a71f75 abb04ae474a1287d c05d2ce0e910c810
        d06e4697fbd625ed d3968273c65ffe22 d548c0a7e202f8b3 df4e699865aaedb6
        e3edf1fb31ab0462 e63eceb94df3b541 ed0d2c38c24d8b4f ef6fab54e01e1b86
        f2be48c5e58fa8a5 f5894f1f4921325d f9d770eff2a9360b
        """
    ),
    "root-cause-analyst.md": _digests(
        """
        00750e6e49e74542 00964df01932b8d5 052495d891f1c270 05515cbb44507d87
        0562f96230c1f460 07624023d8120f5a 07d71c34b558b0da 129c62f41909a07b
        15d7e2a44bd39e08 1aa86b2c7fa0f8cd 1b07538f76797fba 1f41846a8fb208a1
        201edc4576224e75 21c3c485f34eb470 2d792f5c60581295 2d7c4106dfc9a32e
        2dcc2d461bef59db 32d924a79ce3bb7a 3aef640cdbfdf73c 3f76ddb14550080f
        3fff4f26106f01cd 42a87a258bd5c91f 43106e4c3918ba79 4aed089955b3371b
        53e3647be5f06fd7 60f1ba7701515487 61c4d61ad9772df5 63c17901eba5cd55
        6411af463c77e5b3 6b64e8837ff0ba59 6d33b7f6fdb8ac4f 6e0dab7b41e637b7
        6fe5d802ebfaeb6b 76edf49045fe7faf 7809d6f875ddd37e 8b3775d482c0113c
        8dd2d9a212055606 933aa8b396ea1868 9c1361c3b8ab3559 9e9e6e4c02e19d00
        9f87c9f563451a52 a4a4f145ba7ba76f a50efd37883ba021 a89a2f79c400642f
        acad1450f8329f15 aed02ed56daf9a92 b536f7f8b0770ad7 bca6b3122d0fe294
        c0e179f3c4cc2ce5 c6ad4b2b51e76a15 ca3e641e18668086 cceb337a82f9925b
        d9be00d209fd65c8 d9f1fa2b16ec38ce db464a93e75977b0 e78e8a345944fffe
        ef3604a098f3b0e3 f54f3c0c2a57ddd5 f6d46793ee32ba30 f8672fee59617a78
        """
    ),
    "security-engineer.md": _digests(
        """
        010ea6adfa1603fe 0372f81ce255ddb6 09a0f44194688de5 0ae34656f00c9cc9
        0fb45eb20fcd5742 13a2545fe0609028 14b610958aedca95 155089d1571ec8f7
        19109fb36ce1ca7b 1be9d9d92d6a1012 1cf0f8eb0214f363 1e098965ef67ad8d
        1e9cdf005833c340 2055fcf81581422d 21f19428610558e1 226f6c8c196958ba
        31fbc4647a88393d 3f3d04b181853dee 46ec9ffe316ed387 4a7d685fd4dd9b89
        4a9c11b9934bd000 4cb764a31dfb067c 4e8aacee750a66d9 5461b17075bca09d
        5bf5bbd10b572e7b 5c55270a8eabf14b 5c740f2d76d6c7ce 6359d6ceeceb8710
        6408eeca3395887a 6a783858a3e26c2f 6bf666171a13e188 6ce9521de7f5c6ba
        727f85adb30a711d 745c55be05b6338e 74ec465bbaa83372 755db972df303de8
        771ad781c2637f89 78153d6d60da6430 7ae75a13d27dbf16 7bca366d4fba5c19
        7d4d20d317cc8e26 82e5d97dd131882c 8814a8e4d837a1ce 8bec8ddaf2e37531
        8de8a8645b45163a 927d634b863e2315 975f1be89cc7af75 9c167f4936f63d81
        9cf4035d84f4ba7e a62c9d16a58b878f b47193a4a5a7e21f b7c37faa2d8fdd7b
        bf89b99417d3612e c727b17f50ea0235 c788dbbc8c4682ed ca2bb5960589146b
        cc1cc1ee54dc86aa d3a697e843e4aa61 da2fc9f03962b722 db8f90d58477e940
        dcb0210a04ebb884 e1e753fe089c803f eba487ef273174a3 f63f215226a458f1
        f9013e882df8ca00
        """
    ),
    "simplicity-guide.md": _digests(
        """
        00b9799efbedd68f 06f683439ed2778e 0a7e3901bad826fe 0bd1b17a4fff3c7a
        1a25bf9231d33eda 1a95723b52a64e7f 1a99ea85cd5a59eb 1d5092c38714d577
        1e3f24ed59e57e4a 229d0af0aa8f0299 2f6247ede9f3a852 3122af4ad8afb026
        3a2077d1d90ba754 3f5606ce86312b94 418a4a432651982a 4295cc4650e0d61f
        4a313be47608b3fc 562680c7cedba0f1 5f9d0aef866b1808 6d13fe439c31feaa
        72109482f83e238b 7a803d36b82b5ddf 7ad711ef83ed27b7 83cf061a25e4a3d7
        85b31ec66b86fc71 8fb7f7aa11536714 94aff3b86de3f45e 9837929a9fe38c99
        9b298014c07509b7 aa20db62cdc271ce b217cbbd1ebb5c75 b21aba3e31e34342
        b34c83e0bdda8d3d b668e64bb43dc12a b9189ade05b14ac1 c25af8f95e6b5223
        d1894682c5f41a6a d98bd31f48ad3917 ecd61f93a7782236 f061977496fcc662
        f30b509c4ceb3333
        """
    ),
    "socratic-mentor.md": _digests(
        """
        0206195667032204 0403aa1b6f2b96c3 04172b1d72d9b7f9 05e45aaee372f3b6
        06f4faf6d9635d18 08d5c6afb810f700 0cae625d185075e1 10eac3fba65b5bf9
        11acfa4d341fd5fe 1636831a19ff6c4a 16375b7db55172d3 2418ba5518bb8902
        352ba1e407198ea8 39922a97739fb295 3a9bd8cf15442ff2 43563ed094dea416
        44aeed91da9f0150 4eb3a29804e56a84 501e27546ab60de6 5558fa5b988dcba9
        584bd6162b5a537b 5a02689b51137e27 5a90c7bffd32953a 640a84e617809351
        69fab515dd30d1d2 6fbac41bd3e32533 71a14a61743a6414 72b4032fefa3787c
        81c0d389825d471e 83a887f488877f0b 8d3ca1c9f6daf345 8e05ed7a42c12981
        8e394872b6b3e683 94ff698963d24e9a 9bbd4e6e63d9436e a026b42ba7c6ad63
        a16625360667f780 a1ea95e6e123722f a578d69d06282778 a76821ed805ebcb4
        ad4b3a2bf6bf29ab af8ada6ed21e76fc bb3246c36c52959c c2190f16fa4a0ed9
        c2698fa2a5ba551d c4ac305cab6fae98 c5be220fbfb4d610 c6f841d934310348
        c916edca8f1b3a87 cfd230b08f28783f d47ce89c85c6eb89 de29a8b4206932a7
        dff8f2a4d706a0a3 e057c1410cda00a0 e072621ebbf448f6 e08efd67b6eebb1e
        ee2459f7ca69ce83 f08d586c1a8a998e fd9b9299cee5f3aa
        """
    ),
    "system-architect.md": _digests(
        """
        00879849d650f27f 059e2caa88674158 0787b746dbe1e6f6 0b724e258778e997
        11b581de32a16216 138a2721984418aa 21a6d94bdca932e3 2441a79589baf2ce
        244fda45082bded1 2a472aa7bffac570 32d3376ad898bc6a 3ea3d3231b1e765b
        4786fe2148d37daf 4a574654b4177fd3 4b5d57ec82480a3f 4e6e7763a57f1523
        4e8c7badf2299221 51b6b60e68b53b80 5536addefa1c895b 56475eefcdc5d382
        60014c7f5fe372e3 6241fbb341d38cd0 67cd60374dee6469 6eb25512d5555710
        700d0f3299076476 76e9a1f807a8af3f 77712ac8ea034f46 788b24b0d4293921
        7a5d6e24e581387b 83bfa08fe3a3b7d9 8850f77119d6e925 952d83017d1a7cc7
        956ab52314047fab 9f49ac76cec8d131 aa0288cca99ce245 ac9b727614327bff
        ae5bac17b0fa7ecc af632de28b5cb841 b2ceff204d4c1be2 b3b99ce1e347cd4c
        bb4adb10b91bfc10 c4eb516f8136cdc2 c56bed3ce7b9a603 c9a54ad931105b34
        d2a8ff947faea1a1 dab84b5d930451d2 dabf6c638564c596 db11d436852635b3
        dc8d7c61f78db39b dde7645e5582a102 e13fdb5a23fc563e e8cc908018de750c
        eba189ab292f94af ef00886d328399cd f3f6041aa0b00ff0 f8c302436da071ed
        ff9323c611d5b582
        """
    ),
    "technical-writer.md": _digests(
        """
        03f0f97220a6dbb4 0d5ac38728f6e2f4 138712122a4c18aa 13cdee0e67281394
        237eeb0b77e2dad3 25cb4ef9bfda1c48 2b01eabbad2c3266 2e07bd91412c9850
        2ed6d1a4f9de337b 2edef789f4aaa23c 2f429f3000fc97b9 36a112548fdcd024
        3c19a024018e8876 432972cb899c4a89 4719e6662de93cfd 4a549cdad04b6306
        4c96270a93f20ac6 4e03081514f017ba 517a9c4885b66ee2 52290c3887b80394
        52c63da8fba3d5ae 52fb174dcee0b8a6 5e7b5414deffe14a 5e949aadb3e4872a
        5ff41632e5781acc 64a244e2c9b869aa 6640efc971ceae1f 6ceff6ab706153b9
        6f36b504d8a5a485 70c90e0bfd6cf040 77bbc7cc5e93789c 7ebd603d2c1e8bcf
        810fac4bf76104ba 83ce161c5394f86e 840d7d669242092f 8671f093bb6ecdc0
        88391d9f08749ab4 956840387cac6552 975821af81f5c1a3 a67cf02ee3c22e05
        a805aac83e4930aa ad72d8fefd0e26c0 bbe714de9601fe56 bd7a2b4f2c140e10
        c4261afb62599610 c7f1bee591e42991 d051a739fe9221ea d391f3043c947d2c
        e2fed37ae995cf35 e337b474088e4e4f e4feaafe67c4045d f231c56a11449ce0
        f50ed82ddac38444 f66b667bf1800d3f f724c1f854fc1786 f77ff5410dcbf872
        fb2420d8f43d460b fdbb07d8f0a58aff fe3bea78fe4b0846
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
