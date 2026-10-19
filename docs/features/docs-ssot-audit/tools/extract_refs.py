"""Mechanical reference extraction for the docs-ssot audit.

Walks every document in scope, pulls out each checkable claim (a path, a
/sc: command, a CLI subcommand or option, a make target, a hook name, a flag,
a rule citation, an env var, a Python identifier, a markdown link, a count)
and checks it against the SSOT (the file tree, the click app, hook_dispatch,
the Makefile, context_loader's flag tables, RULES_QUALITY.md). Prints one
line per unresolved reference: ``file:line  kind  token  note``.

Run from the repo root: ``uv run python docs/features/docs-ssot-audit/tools/extract_refs.py``.
Read-only. The hits are candidates: 03-findings.md records which survived a
re-read of the cited line.
"""

from __future__ import annotations

import html
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SRC = ROOT / "src" / "superclaude"
sys.path.insert(0, str(ROOT / "src"))

from superclaude.cli import main as cli_main  # noqa: E402
from superclaude.cli.hook_dispatch import HOOKS  # noqa: E402
from superclaude.cli.install_mcp import MCP_SERVERS  # noqa: E402
from superclaude.scripts import context_loader as cl  # noqa: E402

# ---------------------------------------------------------------- scope ----
EXCLUDE_DIRS = ("docs/archive/", "docs/features/", "docs/codex/prompting_session_raw/00_raw")


def docs_in_scope() -> list[Path]:
    files = [ROOT / "README.md", ROOT / "AGENTS.md", ROOT / "CLAUDE.md", ROOT / "CHANGELOG.md"]
    files += sorted((ROOT / "docs").rglob("*.md"))
    files += [ROOT / "docs" / "index.html"]
    files += sorted((ROOT / ".claude" / "rules").rglob("*.md"))
    files += sorted(SRC.rglob("*.md"))
    files += [ROOT / "Makefile"]
    out = []
    for f in files:
        rel = f.relative_to(ROOT).as_posix()
        if any(rel.startswith(x) for x in EXCLUDE_DIRS):
            continue
        if "__pycache__" in rel:
            continue
        out.append(f)
    return out


def feature_docs() -> list[Path]:
    """docs/features/** — link check only (stale cross-links)."""
    return sorted(p for p in (ROOT / "docs" / "features").rglob("*.md"))


# ---------------------------------------------------------------- ssot -----
COMMANDS = {p.stem for p in (SRC / "commands").glob("*.md") if p.name != "README.md"}
AGENTS = {p.stem for p in (SRC / "agents").glob("*.md") if p.name != "README.md"}
SKILLS = {p.name for p in (SRC / "skills").iterdir() if p.is_dir()}
MAKE_TARGETS = set(
    re.search(r"^\.PHONY:(.*)$", (ROOT / "Makefile").read_text(), re.M).group(1).split()
)
CLI_COMMANDS = set(cli_main.main.commands)
CLI_OPTIONS: dict[str, set[str]] = {}
for name, cmd in cli_main.main.commands.items():
    opts = set()
    for p in cmd.params:
        opts.update(getattr(p, "opts", []))
        opts.update(getattr(p, "secondary_opts", []))
    CLI_OPTIONS[name] = opts
CLI_OPTIONS["context"] = {"--session"}
INSIGHT_SUBS = {
    "append", "list", "query", "stats", "harvest", "review", "promote", "discard",
    "pending-count", "session-baseline", "request",
    "harvest-from-hook", "pending-count-from-hook", "request-from-hook",
}
CONTEXT_SUBS = {"explain", "reset"}
COMMAND_LOCAL_FLAGS: set[str] = set()
for p in (SRC / "commands").glob("*.md"):
    COMMAND_LOCAL_FLAGS |= cl.flag_entries(p.read_text(encoding="utf-8"))
    m = re.search(r"<syntax>(.*?)</syntax>", p.read_text(encoding="utf-8"), re.S)
    if m:
        COMMAND_LOCAL_FLAGS |= {f for f in re.findall(r"--([a-z][\w-]*)", m.group(1))}
KNOWN_FLAGS = (
    set(cl.VALID_FLAGS) | set(cl.RETIRED_FLAGS) | set(cl.CC_NATIVE_PASSTHROUGH) | COMMAND_LOCAL_FLAGS
)
for opts in CLI_OPTIONS.values():
    KNOWN_FLAGS |= {o.lstrip("-") for o in opts if o.startswith("--")}
# Flags of other tools that docs legitimately name.
FOREIGN_FLAGS = {
    "force", "force-with-lease", "hard", "no-rebase", "editable", "system", "dry-run",
    "version", "help", "ignore", "tb", "strict-markers", "trace-config", "collect-only",
    "color", "cached", "no-ff", "no-sync", "project", "offline", "from", "model", "effort",
    "permission-mode", "runs-dir", "canary", "task", "no-deps", "python", "upgrade",
    "print", "json", "jq", "ref", "workflow", "status", "commit", "event", "exit-status",
    "target", "title", "notes-file", "tags", "abbrev", "match", "name-only", "quiet",
    "show-current", "is-ancestor", "delete", "check", "cov", "p", "add-dir",
    "out-dir", "budget", "metric", "eval-cmd", "smoke-cmd", "mutator-model",
    "cycle-timeout", "type", "format", "with", "session", "servers", "list", "list-all",
    "scope", "keep-settings", "remove-mcp", "yes", "interactive", "verbose", "caps",
    "dangerously-skip-permissions", "output-format", "resume", "continue", "agent",
    "append-system-prompt", "settings", "mcp-config", "allowedTools", "allowed-tools",
    "disallowedTools", "max-turns", "input-format", "session-id", "worktree", "bare",
    "no-cache", "frozen", "locked", "reinstall", "refresh", "index", "all", "stat",
    "oneline", "graph", "decorate", "amend", "message", "file", "patch", "staged",
    "global", "local", "unset", "get", "porcelain", "short", "branch", "show", "prune",
    "fetch", "pull", "push", "tags", "user", "exclude", "include", "grep", "fixed-strings",
    "line-number", "count", "files-with-matches", "recursive", "extended-regexp",
    "ignore-case", "null", "max-count", "after-context", "before-context", "context",
    "sort", "reverse", "numeric-sort", "unique", "zero", "max-depth", "name", "path",
    "exec", "newer", "mindepth", "maxdepth", "model-override", "max-findings", "fix",
    "comment", "post", "no-post", "md", "xml", "pr-bundle", "audit-delegated",
    "structured", "strategy", "depth", "loop", "iterations", "focus", "introspect",
    "ultrathink", "think", "think-hard", "seq", "sequential", "parallel",
    "runs", "arm", "arms", "limit", "ids", "write", "apply", "plan",
}

RULES_QUALITY = (SRC / "core" / "rules" / "RULES_QUALITY.md").read_text(encoding="utf-8")
RULE_DEFS = dict(re.findall(r"\[(R\d\d) ([^\]]+)\]", RULES_QUALITY))
TESTS = {p.name for p in (ROOT / "tests").rglob("test_*.py")}
TEST_PATHS = {p.relative_to(ROOT).as_posix() for p in (ROOT / "tests").rglob("*.py")}

SEARCH_TEXT_CACHE: dict[str, bool] = {}


def grep_exists(token: str) -> bool:
    """True when ``token`` occurs as a whole word anywhere code-like in the repo."""
    if token in SEARCH_TEXT_CACHE:
        return SEARCH_TEXT_CACHE[token]
    r = subprocess.run(
        ["grep", "-rqw", "--include=*.py", "--include=*.json", "--include=*.yaml",
         "--include=*.yml", "--include=Makefile", "--include=*.toml", "--include=*.sh",
         "--include=*.ps1", "-e", token,
         "src", "tests", "scripts", "evals", "Makefile", "pyproject.toml", ".github", "portable-skills", ".claude-plugin"],
        cwd=ROOT,
    )
    SEARCH_TEXT_CACHE[token] = r.returncode == 0
    return SEARCH_TEXT_CACHE[token]


# ---------------------------------------------------------------- paths ----
PLACEHOLDER = re.compile(r"[<>{}*…$|]|\.\.\.|\bNN\b|<slug>|YYYY")
PATH_TOKEN = re.compile(
    r"^(?:\./|~/)?[\w.@+-]+(?:/[\w.@+\-*]+)*/?(?::\d+(?:-\d+)?)?(?:::\w+)?$"
)
SUFFIXES = (".md", ".py", ".json", ".yaml", ".yml", ".sh", ".toml", ".ps1", ".html", ".txt", ".jsonl", ".zip")
INSTALL_ROOTS = ("~/.claude/", ".claude/", "<scope>/", "<base>/")


def resolve_path(token: str) -> tuple[bool, str]:
    """Return (resolved, normalized) for a doc path token."""
    t = token.strip("`'\" ")
    t = re.sub(r"(::\w+|:\d+(?:-\d+)?)$", "", t)
    t = t.rstrip("/")
    if t.startswith("./"):
        t = t[2:]
    if t.startswith("http") or t.startswith("mailto"):
        return True, t
    if t.startswith("~/.claude/") or t.startswith("~/.claude.json") or t == "~/.claude":
        # install-tree path: map to source when it names shipped content
        rest = t[len("~/.claude/"):]
        return resolve_install_path(rest), t
    if t.startswith(".claude/") and not (ROOT / t).exists():
        return resolve_install_path(t[len(".claude/"):]), t
    if PLACEHOLDER.search(t):
        return True, t
    candidates = [ROOT / t, SRC / t, SRC / "core" / t, ROOT / "docs" / t, ROOT / ".claude" / t,
                  ROOT / ".claude" / "rules" / t, ROOT / "tests" / t, ROOT / "tests" / "unit" / t,
                  SRC / "cli" / t, SRC / "scripts" / t, SRC / "commands" / t, SRC / "agents" / t,
                  SRC / "modes" / t, SRC / "mcp" / t, SRC / "core" / "rules" / t, SRC / "skills" / t,
                  ROOT / "evals" / t, ROOT / "docs" / "features" / t]
    if any(c.exists() for c in candidates):
        return True, t
    # bare file name anywhere in the tree
    name = Path(t).name
    if "/" not in t and (list(ROOT.rglob(name))):
        return True, t
    return False, t


def resolve_install_path(rest: str) -> bool:
    """Map an installed path (commands/sc/x.md, superclaude/core/x.md, agents/x.md) to the source."""
    rest = rest.rstrip("/")
    if PLACEHOLDER.search(rest):
        return True
    runtime = ("settings.json", "settings.local.json", "CLAUDE.md", "insights.jsonl",
               "insights.pending.jsonl", "memories", "agent-memory", "agent-memory-local",
               ".superclaude_hooks", "hooks/hooks.json", "hooks", "skills", "commands", "agents",
               "output-styles", "superclaude", "projects", "rules", "commands/sc", "worktrees")
    if rest in runtime or rest.startswith((".superclaude_hooks", "projects/", "memories/", "agent-memory", "rules/")):
        return True
    m = {
        "commands/sc/": SRC / "commands",
        "superclaude/core/rules/": SRC / "core" / "rules",
        "superclaude/core/": SRC / "core",
        "superclaude/modes/": SRC / "modes",
        "superclaude/mcp/": SRC / "mcp",
        "superclaude/templates/": SRC / "templates",
        "superclaude/scripts/": SRC / "scripts",
        "agents/": SRC / "agents",
        "output-styles/": SRC / "output-styles",
        "skills/": SRC / "skills",
    }
    for prefix, d in m.items():
        if rest.startswith(prefix):
            tail = rest[len(prefix):]
            if not tail:
                return True
            if prefix == "superclaude/scripts/":
                return True  # legacy copies: documented as leftovers
            return (d / tail).exists()
    if rest == "superclaude/CLAUDE_SC.md":
        return True
    return (ROOT / ".claude" / rest).exists()


# ---------------------------------------------------------------- walk -----
BACKTICK = re.compile(r"`([^`\n]+)`")
MD_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
SC_CMD = re.compile(r"/sc:([a-zA-Z][\w-]*)")
SC_SKILL = re.compile(r"/sc-([a-z][\w-]*)")
SUPERCLAUDE_CMD = re.compile(r"\bsuperclaude\s+([a-z][\w-]*)(?:\s+([a-z][\w-]*))?((?:\s+-{1,2}[\w-]+)*)")
MAKE_CMD = re.compile(r"\bmake\s+([a-z][\w-]*)")
HOOK_CMD = re.compile(r"superclaude hook ([a-z_]+)")
FLAG = re.compile(r"(?<![\w/-])--([a-z][\w-]*)")
RULE_CIT = re.compile(r"\[(R\d\d) ([^\]]+)\]")
RULE_BARE = re.compile(r"(?<![\w-])(R\d\d)(?![\w-])")
ENV_VAR = re.compile(r"\b((?:SUPERCLAUDE|CLAUDE_CONTEXT|CLAUDE_CODE|CLAUDE_CONFIG|CLAUDE_PROJECT|TAVILY|GH|CANARY|EVAL|MYPY)_[A-Z0-9_]+)\b")
IDENT = re.compile(r"^(?:[a-z_][a-z0-9_]*\.)*([A-Za-z_][A-Za-z0-9_]*)(\(\))?$")
COUNT = re.compile(
    r"\b(\d+)\s+(?:(?:shipped|slash|specialized|adaptive|behavioral|domain-expert|managed|distinct|console|inner|hard-gate|rule)\s+)?"
    r"(slash commands|commands|agents|agent definitions|modes|MCP servers|servers|hooks|hook registrations|registrations|hook entry scripts|skills|output styles|rule modules|rule classes|guards|arms?|tasks)\b",
    re.I,
)
AT_AGENT = re.compile(r"(?<![\w.])@([a-z][a-z0-9-]+)\b")
RETIRED_MCP = re.compile(r"\b(serena|morphllm|mindbase|airis|magic|ast-grep|sequential-thinking|sequential thinking)\b", re.I)
BRANCH_INTEGRATION = re.compile(r"`integration`|\bintegration branch\b|master.*integration")
COUNTS = {
    "slash commands": len(COMMANDS), "commands": len(COMMANDS), "agents": len(AGENTS),
    "agent definitions": len(AGENTS), "modes": 6, "mcp servers": len(MCP_SERVERS), "servers": len(MCP_SERVERS),
    "hooks": 14, "hook registrations": 14, "registrations": 14, "hook entry scripts": len(HOOKS),
    "skills": len(SKILLS), "output styles": 1, "rule modules": 4, "rule classes": 5, "guards": 3,
}


def html_lines(path: Path) -> list[str]:
    t = path.read_text(encoding="utf-8")
    t = re.sub(r"<script.*?</script>", "", t, flags=re.S)
    t = re.sub(r"<style.*?</style>", "", t, flags=re.S)
    return [html.unescape(re.sub(r"<[^>]+>", "", l)) for l in t.split("\n")]


def main() -> None:
    hits: list[tuple[str, int, str, str, str]] = []

    def hit(path: Path, ln: int, kind: str, token: str, note: str = "") -> None:
        hits.append((path.relative_to(ROOT).as_posix(), ln, kind, token, note))

    for path in docs_in_scope():
        rel = path.relative_to(ROOT).as_posix()
        shipped = rel.startswith("src/superclaude/")
        lines = html_lines(path) if path.suffix == ".html" else path.read_text(encoding="utf-8").split("\n")
        in_fence = False
        for ln, line in enumerate(lines, 1):
            if line.strip().startswith("```"):
                in_fence = not in_fence
            # /sc:command
            for m in SC_CMD.finditer(line):
                name = m.group(1)
                if name not in COMMANDS and name not in ("X", "x", "name", "command", "cmd"):
                    hit(path, ln, "sc-command", f"/sc:{name}", "no commands/<name>.md")
            for m in SC_SKILL.finditer(line):
                if f"sc-{m.group(1)}" not in SKILLS:
                    hit(path, ln, "sc-skill", f"/sc-{m.group(1)}", "no skills/<name>/")
            # superclaude <sub> [<sub2>] [--opts]
            for m in SUPERCLAUDE_CMD.finditer(line):
                sub, sub2, opts = m.group(1), m.group(2), m.group(3) or ""
                if sub in ("install", "uninstall", "update", "mcp", "doctor", "verify-drift", "author-check",
                           "insight", "hook", "auto-improve", "parallel-ab", "context"):
                    if sub == "hook" and sub2 and sub2 not in HOOKS and sub2 not in ("<name>", "name"):
                        hit(path, ln, "hook-name", f"superclaude hook {sub2}", "not in hook_dispatch.HOOKS")
                    if sub == "insight" and sub2 and sub2 not in INSIGHT_SUBS:
                        hit(path, ln, "insight-sub", f"superclaude insight {sub2}", "not an insight subcommand")
                    if sub == "context" and sub2 and sub2 not in CONTEXT_SUBS:
                        hit(path, ln, "context-sub", f"superclaude context {sub2}", "not a context subcommand")
                    for o in re.findall(r"(-{1,2}[\w-]+)", opts):
                        if sub in CLI_OPTIONS and o not in CLI_OPTIONS[sub] and o not in ("--help", "-h"):
                            hit(path, ln, "cli-option", f"superclaude {sub} {o}", "option not on that subcommand")
                elif sub in ("is", "on", "now", "and", "the", "CLI", "content", "components", "doctor", "hooks",
                             "command", "commands", "framework", "config", "skill", "skills", "install-skill",
                             "hook", "started", "ships", "turns", "builds", "reads", "cli", "inner",
                             "version", "package", "repository", "registers", "writes", "to", "in", "at", "with",
                             "that", "from", "of", "for", "import", "block", "setup", "by", "via", "files",
                             "or", "as", "if", "then", "project", "agent", "agents", "settings", "dir", "tool",
                             "process", "prompts", "home", "marketplace", "distribution", "user", "scripts",
                             "mode", "modes", "plugin", "pytest", "components", "commands", "markers", "runtime",
                             "content", "core", "install", "has", "does", "itself", "yet", "never", "says",
                             "was", "will", "would", "should", "can", "cannot", "did", "loads", "only", "no",
                             "ctx", "run", "cache", "state", "memory", "insights", "feature", "header"):
                    pass
                elif sub in ("pm", "hooks", "insight", "install-skill", "sync", "deploy", "init", "check",
                             "prompt", "status", "list", "version", "verify", "drift", "sc", "author", "test",
                             "upgrade", "sync-user", "setup", "configure"):
                    hit(path, ln, "cli-sub", f"superclaude {sub}", "not a CLI subcommand")
            for m in MAKE_CMD.finditer(line):
                t = m.group(1)
                if t not in MAKE_TARGETS and t not in ("the", "a", "it", "sure", "sense", "them", "up", "is", "no",
                                                       "an", "you", "your", "its", "this", "that", "one",
                                                       "each", "every", "any", "all", "two", "both", "changes",
                                                       "sync", "runs", "lines", "edits", "our", "these", "those",
                                                       "and", "or", "me", "him", "her", "us", "room", "it", "ci"):
                    if t in ("test", "lint", "format", "deploy", "install", "sync-user", "sync-project",
                             "sync-local", "help", "doctor", "clean", "release", "ci", "typecheck", "verify",
                             "verify-drift", "canary", "canary-gates", "uninstall", "uninstall-user",
                             "uninstall-legacy", "test-scripts", "test-plugin", "check", "setup", "dev",
                             "build", "publish", "sync", "mypy"):
                        hit(path, ln, "make-target", f"make {t}", "not a Makefile target")
            # paths in backticks and links
            tokens = [t for t in BACKTICK.findall(line)] + [t for t in MD_LINK.findall(line)]
            for tok in tokens:
                raw = tok.strip()
                if raw.startswith("#") or raw.startswith("http") or raw.startswith("mailto"):
                    continue
                core = re.sub(r"\s+§.*$", "", raw).split(" ")[0] if " " in raw and "/" in raw.split(" ")[0] else raw
                if " " in core:
                    continue
                looks_path = ("/" in core and not core.startswith("/sc") and not core.startswith("--")) or core.endswith(SUFFIXES)
                if not looks_path:
                    continue
                if not PATH_TOKEN.match(core) and not core.startswith("~/"):
                    continue
                if core.startswith(("/btw", "/goal", "/plugin", "/config", "/effort", "/doctor", "/socratic", "/clear", "/compact", "/exit", "/help", "/agents", "/memory", "/rewind", "/fast", "/loop", "/code-review", "/skill", "/ultrareview", "/init", "/sc", "/", "docs@")):
                    continue
                if re.fullmatch(r"[\w.-]+/[\w.-]+@[\w.-]+", core) or "@" in core:
                    continue
                if re.fullmatch(r"\d+/\d+", core) or re.fullmatch(r"[\d.]+(/[\d.+]+)+", core):
                    continue
                if core.count("/") == 1 and re.fullmatch(r"[a-z]+/[a-z]+", core) and "." not in core and not (ROOT / core).exists() and not (SRC / core).exists():
                    # word/word pairs (user/project), skip unless it names a dir
                    continue
                if path.suffix == ".md" and raw in MD_LINK.findall(line):
                    # relative link: resolve against the file's own directory first
                    target = (path.parent / core.split("#")[0]).resolve()
                    if target.exists():
                        continue
                ok, norm = resolve_path(core)
                if not ok:
                    hit(path, ln, "path", norm, "does not resolve")
            # flags in non-shipped docs and in shipped READMEs
            if not shipped or path.name == "README.md" or path.name == "ARCHITECTURE.md":
                for m in FLAG.finditer(line):
                    f = m.group(1)
                    if f not in KNOWN_FLAGS and f not in FOREIGN_FLAGS and not in_fence:
                        hit(path, ln, "flag", f"--{f}", "not a known SC/CLI/command-local flag")
            # rule citations
            if not shipped:
                for m in RULE_CIT.finditer(line):
                    rid, name = m.group(1), m.group(2)
                    if RULE_DEFS.get(rid) != name:
                        hit(path, ln, "rule-cite", m.group(0), f"defined as {rid} {RULE_DEFS.get(rid)!r}")
                for m in RULE_BARE.finditer(line):
                    rid = m.group(1)
                    if rid not in RULE_DEFS and rid not in ("R19",):
                        hit(path, ln, "rule-id", rid, "no such rule id")
            # env vars
            for m in ENV_VAR.finditer(line):
                v = m.group(1)
                if not grep_exists(v):
                    hit(path, ln, "env-var", v, "not found in code")
            # identifiers in backticks
            for tok in BACKTICK.findall(line):
                t = tok.strip()
                m = IDENT.match(t)
                if not m:
                    continue
                name, call = m.group(1), m.group(2)
                if ("_" in name or call) and len(name) > 3 and not name.startswith("sc_"):
                    if name.lower() in ("sc_", "my_", "x_", "foo_bar", "snake_case", "critical_", "upper_snake", "mode_", "mcp_", "rules_", "section_one", "section_two", "sub_section_a", "sub_section_b", "named_enum_section", "ordered_procedure_section", "fixed_label_section", "root_wrapper", "label_a", "label_b", "label_c", "n_of", "k_", "tool_guidance", "memory_guide", "doc_output_convention", "flag_matrix", "error_codes", "sub_agent_decision", "purpose_before_action", "scope_discipline", "test_name", "test_file", "shipped_now", "hook_ids", "hook_events", "claude_base", "hook_state_dir", "project_root", "project_key", "main_worktree_root"):
                        continue
                    if name.isupper() or call or re.match(r"^[a-z]+_[a-z_]+$", name):
                        if not grep_exists(name):
                            hit(path, ln, "identifier", t, "not found in code")
            # counts
            for m in COUNT.finditer(line):
                n, what = int(m.group(1)), m.group(2).lower()
                exp = COUNTS.get(what)
                if exp is not None and n != exp:
                    hit(path, ln, "count", f"{n} {what}", f"source has {exp}")
            # @agent
            for m in AT_AGENT.finditer(line):
                a = m.group(1)
                if a not in AGENTS and a not in ("stable", "superclaude", "import", "v", "master", "main", "agents", "latest", "click", "pytest", "ajitta", "chosh1179", "anthropic-ai", "playwright", "import") and not a.startswith(("v4", "v5")):
                    if a in ("pm-agent", "deep-research-agent", "repo-index", "deep-researcher", "verifier", "self-review", "reviewer", "explore", "plan", "general-purpose") and a not in AGENTS:
                        hit(path, ln, "agent", f"@{a}", "no agents/<name>.md")
            # retired MCP names in shipped content
            if shipped and RETIRED_MCP.search(line):
                hit(path, ln, "retired-mcp", RETIRED_MCP.search(line).group(1), "retired server named in shipped content")
            if BRANCH_INTEGRATION.search(line) and "branch" in line.lower():
                hit(path, ln, "branch", line.strip()[:80], "names an integration branch")
            # test file references
            for m in re.finditer(r"\btests?/[\w/]+\.py\b|\btest_[\w]+\.py\b", line):
                t = m.group(0)
                if t.startswith("tests/") or t.startswith("test/"):
                    if t not in TEST_PATHS and not PLACEHOLDER.search(t):
                        hit(path, ln, "test-path", t, "no such test file")
                elif t not in TESTS and not PLACEHOLDER.search(t):
                    hit(path, ln, "test-file", t, "no such test file")

    # docs/features cross-links (stale cross-link note only)
    for path in feature_docs():
        for ln, line in enumerate(path.read_text(encoding="utf-8").split("\n"), 1):
            for tgt in MD_LINK.findall(line):
                if tgt.startswith(("http", "#", "mailto")):
                    continue
                t = tgt.split("#")[0]
                if not t or PLACEHOLDER.search(t):
                    continue
                if not (path.parent / t).resolve().exists() and not (ROOT / t).exists():
                    hit(path, ln, "feature-link", tgt, "broken relative link")

    for rel, ln, kind, token, note in sorted(hits):
        print(f"{rel}:{ln}\t{kind}\t{token}\t{note}")
    print(f"\n{len(hits)} candidate hits", file=sys.stderr)


if __name__ == "__main__":
    main()
