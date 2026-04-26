"""
MCP Server Installation Module for SuperClaude

Installs and manages MCP servers using the latest Claude Code API.
Based on the installer logic from commit d4a17fc but adapted for modern Claude Code.
"""

import json
import os
import platform
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import click

# MCP Server Registry
# Adapted from commit d4a17fc with modern transport configuration
MCP_SERVERS = {
    "sequential-thinking": {
        "name": "sequential-thinking",
        "description": "Multi-step problem solving and systematic analysis",
        "transport": "stdio",
        "command": "npx -y @modelcontextprotocol/server-sequential-thinking",
        "required": False,
    },
    "context7": {
        "name": "context7",
        "description": "Official library documentation and code examples",
        "transport": "stdio",
        "command": "npx -y @upstash/context7-mcp",
        "required": False,
    },
    "serena": {
        "name": "serena",
        "description": "Semantic code analysis and intelligent editing",
        "transport": "stdio",
        "command": "serena start-mcp-server --context=claude-code --project-from-cwd",
        "required": False,
    },
    "tavily": {
        "name": "tavily",
        "description": "Web search and real-time information retrieval for deep research",
        "transport": "stdio",
        "command": "npx -y mcp-remote https://mcp.tavily.com/mcp",
        "required": False,
        "api_key_env": "TAVILY_API_KEY",
        "api_key_description": "Tavily API key for web search (get from https://app.tavily.com)",
        "api_key_in_url": True,
        "api_key_url_param": "tavilyApiKey",  # URL param name (camelCase)
    },
    "ast-grep": {
        "name": "ast-grep",
        "description": "Structural AST pattern search and code analysis using tree-sitter",
        "transport": "stdio",
        "command": "uvx --from git+https://github.com/ast-grep/ast-grep-mcp ast-grep-server",
        "required": False,
    },
}


def _mask_secret(text: str, secret: Optional[str]) -> str:
    """Replace a secret value with a masked version in text.

    Args:
        text: Text that may contain the secret
        secret: The secret to mask (if None, returns text unchanged)

    Returns:
        Text with secret replaced by masked version (last 4 chars visible)
    """
    if not secret or secret not in text:
        return text
    masked = f"***{secret[-4:]}" if len(secret) > 4 else "****"
    return text.replace(secret, masked)


def _mask_secrets_in_args(args: List[str], secret: Optional[str]) -> List[str]:
    """Mask secrets in a list of command arguments.

    Args:
        args: Command argument list
        secret: The secret to mask

    Returns:
        New list with secrets masked
    """
    if not secret:
        return args
    return [_mask_secret(arg, secret) for arg in args]


def _run_command(cmd: List[str], **kwargs) -> subprocess.CompletedProcess:
    """
    Run a command with proper cross-platform shell handling.

    Args:
        cmd: Command as list of strings
        **kwargs: Additional subprocess.run arguments

    Returns:
        CompletedProcess result
    """
    # Ensure UTF-8 encoding on all platforms to handle Unicode output
    if "encoding" not in kwargs:
        kwargs["encoding"] = "utf-8"
    if "errors" not in kwargs:
        kwargs["errors"] = "replace"  # Replace undecodable bytes instead of raising

    if platform.system() == "Windows":
        # On Windows, wrap command in 'cmd /c' to properly handle commands like npx
        cmd = ["cmd", "/c"] + cmd
    return subprocess.run(cmd, **kwargs)


def check_prerequisites() -> Tuple[bool, List[str]]:
    """Check if required tools are available."""
    errors = []

    # Check Claude CLI
    try:
        result = _run_command(
            ["claude", "--version"], capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            errors.append("Claude CLI not found - required for MCP server management")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        errors.append("Claude CLI not found - required for MCP server management")

    # Check Node.js for npm-based servers
    try:
        result = _run_command(
            ["node", "--version"], capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            errors.append("Node.js not found - required for npm-based MCP servers")
        else:
            version = result.stdout.strip()
            try:
                version_num = int(version.lstrip("v").split(".")[0])
                if version_num < 18:
                    errors.append(
                        f"Node.js version {version} found, but version 18+ required"
                    )
            except (ValueError, IndexError):
                pass
    except (subprocess.TimeoutExpired, FileNotFoundError):
        errors.append("Node.js not found - required for npm-based MCP servers")

    # Check uv for Python-based servers (optional)
    try:
        result = _run_command(
            ["uv", "--version"], capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            click.echo("⚠️  uv not found - required for Serena MCP server", err=True)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        click.echo("⚠️  uv not found - required for Serena MCP server", err=True)

    # Check ast-grep binary for AST-based MCP server (optional)
    _ast_grep_found = False
    for binary in ["sg", "ast-grep"]:
        try:
            result = _run_command(
                [binary, "--version"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                _ast_grep_found = True
                break
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue
    if not _ast_grep_found:
        click.echo("⚠️  ast-grep not found - required for ast-grep MCP server", err=True)
        click.echo(
            "   Install: brew install ast-grep (macOS) | cargo install ast-grep --locked | npm i -g @ast-grep/cli",
            err=True,
        )

    return len(errors) == 0, errors


def _read_json_safe(path: Path) -> dict:
    """Read a JSON file, returning {} on any error (missing/invalid/unreadable)."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}


def _scope_config_path(
    scope: str, project_root: Optional[Path] = None
) -> Tuple[Path, List[str]]:
    """
    Return (config_file, keypath) for a given MCP scope.

    The keypath is the sequence of dict keys leading to the mcpServers dict.
    Project root defaults to CWD when omitted.
    """
    if scope == "user":
        return Path.home() / ".claude.json", ["mcpServers"]
    if scope == "project":
        root = project_root or Path.cwd()
        return root.resolve() / ".mcp.json", ["mcpServers"]
    if scope == "local":
        root = project_root or Path.cwd()
        project_key = str(root.resolve())
        return Path.home() / ".claude.json", ["projects", project_key, "mcpServers"]
    raise ValueError(f"Unknown MCP scope: {scope!r}")


def _mcp_servers_in_scope(
    scope: str, project_root: Optional[Path] = None
) -> Dict[str, dict]:
    """Return the mcpServers dict at the given scope (empty dict if none)."""
    path, keypath = _scope_config_path(scope, project_root)
    data = _read_json_safe(path)
    for key in keypath:
        if not isinstance(data, dict):
            return {}
        data = data.get(key, {})
    return data if isinstance(data, dict) else {}


SERENA_EXPECTED_FLAG = "--project-from-cwd"
SERENA_STALE_FLAGS = ("--enable-web-dashboard", "--enable-gui-log-window")


def _is_serena_stale_entry(entry: Dict) -> bool:
    """
    Return True if a Serena MCP entry is from the pre-realignment install command.

    Stale signals (any one is sufficient):
      - Missing the `--project-from-cwd` flag in command/args
      - Presence of `--enable-web-dashboard` or `--enable-gui-log-window` (PR #2 dropped these)

    The entry shape is whatever `_mcp_servers_in_scope()` returns — typically a dict
    with keys like `command`, `args`. Both string-form `command` and list-form `args`
    are inspected so we work across both `claude mcp add` styles.
    """
    if not isinstance(entry, dict):
        return False

    parts: List[str] = []
    cmd = entry.get("command")
    if isinstance(cmd, str):
        parts.extend(shlex.split(cmd))
    args = entry.get("args")
    if isinstance(args, list):
        parts.extend(str(a) for a in args)

    if not parts:
        # No usable command info — treat as not-stale (avoid false-positive migration)
        return False

    joined = " ".join(parts)
    if any(flag in joined for flag in SERENA_STALE_FLAGS):
        return True
    if SERENA_EXPECTED_FLAG not in joined:
        return True
    return False


def _migrate_stale_serena(scope: str) -> Tuple[bool, str]:
    """
    Run `claude mcp remove --scope <scope> serena` so the caller can re-install with new flags.

    Returns (success, message). Mirrors the pattern in `uninstall_mcp_servers()`.
    """
    cmd = ["claude", "mcp", "remove", "--scope", scope, "serena"]
    try:
        result = _run_command(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            return True, "Removed stale Serena MCP entry"
        err = (result.stderr or "").strip() or "unknown error"
        return False, f"Failed to remove stale Serena: {err}"
    except (
        subprocess.TimeoutExpired,
        subprocess.SubprocessError,
        FileNotFoundError,
    ) as e:
        return False, f"Failed to remove stale Serena: {e}"


def _handle_stale_serena(scope: str, dry_run: bool) -> Tuple[str, bool]:
    """
    Decide what to do when a stale Serena MCP entry is detected at install-time.

    Returns (action, should_continue):
      - action ∈ {"migrate", "skip", "dry-run"}
      - should_continue: True if the caller should proceed to install the fresh entry
    """
    click.echo("   ⚠️  Stale Serena MCP install detected (pre-realignment flags)")

    if dry_run:
        click.echo(f"   [DRY RUN] Would run: claude mcp remove --scope {scope} serena")
        click.echo("   [DRY RUN] Then re-install Serena with the new flag set")
        return "dry-run", False

    if not sys.stdin.isatty():
        click.echo(
            "   ❌ Cannot prompt for migration in non-interactive context.",
            err=True,
        )
        click.echo(
            f"   To migrate manually, run:\n"
            f"     claude mcp remove --scope {scope} serena\n"
            f"   then re-run this install.",
            err=True,
        )
        return "skip", False

    if not click.confirm(
        "   Migrate now? (runs 'claude mcp remove serena' then re-installs)",
        default=True,
    ):
        click.echo(
            f"   Skipped migration. Run manually when ready:\n"
            f"     claude mcp remove --scope {scope} serena"
        )
        return "skip", False

    success, message = _migrate_stale_serena(scope)
    if success:
        click.echo(f"   ✅ {message}")
        return "migrate", True
    click.echo(f"   ❌ {message}", err=True)
    return "skip", False


def check_mcp_server_installed(
    server_name: str,
    scope: Optional[str] = None,
    project_root: Optional[Path] = None,
) -> bool:
    """
    Check if an MCP server is installed.

    When scope is given, checks that scope only by reading the backing config
    file directly (~/.claude.json or <project>/.mcp.json). When scope is None,
    falls back to scope-agnostic detection via `claude mcp list`.
    """
    if scope is not None:
        return server_name in _mcp_servers_in_scope(scope, project_root)

    try:
        result = _run_command(
            ["claude", "mcp", "list"], capture_output=True, text=True, timeout=60
        )

        if result is None or result.returncode != 0:
            return False

        # Handle case where stdout might be None
        output = result.stdout
        if output is None:
            return False

        return server_name.lower() in output.lower()

    except (subprocess.TimeoutExpired, subprocess.SubprocessError):
        return False


def prompt_for_api_key(
    server_name: str, env_var: str, description: str
) -> Optional[str]:
    """Prompt user for API key if needed."""
    # Check if already set in environment - use silently
    if os.getenv(env_var):
        click.echo(f"   ✅ Using {env_var} from environment")
        return os.getenv(env_var)

    # Not set - prompt user
    click.echo(f"\n🔑 MCP server '{server_name}' requires an API key")
    click.echo(f"   Environment variable: {env_var}")
    click.echo(f"   Description: {description}")

    if click.confirm(f"   Would you like to set {env_var} now?", default=True):
        api_key = click.prompt(f"   Enter {env_var}", hide_input=True)
        return api_key
    else:
        click.echo(
            f"   ⚠️  Proceeding without {env_var} - server may not function properly"
        )
        return None


def install_mcp_server(
    server_info: Dict, scope: str = "user", dry_run: bool = False
) -> bool:
    """
    Install a single MCP server using modern Claude Code API.

    Args:
        server_info: Server configuration dictionary
        scope: Installation scope (local, project, user)
        dry_run: If True, only show what would be done

    Returns:
        True if successful, False otherwise
    """
    server_name = server_info["name"]
    transport = server_info["transport"]
    command = server_info["command"]

    click.echo(f"📦 Installing MCP server: {server_name}")

    # Check if already installed at this specific scope
    if check_mcp_server_installed(server_name, scope=scope):
        # Serena-specific staleness check: PR #2 changed the install command;
        # detect pre-realignment entries (missing --project-from-cwd or stale --enable-* flags)
        # and offer migration. Other servers fall through to the unchanged "already installed" path.
        if server_name == "serena":
            entry = _mcp_servers_in_scope(scope).get(server_name, {})
            if _is_serena_stale_entry(entry):
                _, should_continue = _handle_stale_serena(scope=scope, dry_run=dry_run)
                if not should_continue:
                    return (
                        True  # Skip / declined / dry-run: leave existing install alone
                    )
                # Migration succeeded — fall through to re-install with new flags
            else:
                click.echo(f"   ✅ Already installed at {scope} scope: {server_name}")
                return True
        else:
            click.echo(f"   ✅ Already installed at {scope} scope: {server_name}")
            return True

    # Handle API key requirements
    env_args = []
    api_key = None
    if "api_key_env" in server_info:
        api_key_env = server_info["api_key_env"]
        api_key = prompt_for_api_key(
            server_name,
            api_key_env,
            server_info.get("api_key_description", f"API key for {server_name}"),
        )

        # Check if API key should be in URL or as env var
        if api_key and server_info.get("api_key_in_url"):
            # Append API key to URL in command (for mcp-remote style)
            url_param = server_info.get("api_key_url_param", api_key_env)
            if "?" in command:
                command = f"{command}&{url_param}={api_key}"
            else:
                command = f"{command}?{url_param}={api_key}"
        elif api_key:
            # Standard env var approach
            env_args = ["--env", f"{api_key_env}={api_key}"]

    # Build installation command using modern Claude Code API
    # Format: claude mcp add --transport <transport> --scope <scope> <name> [--env KEY=VALUE] -- <command>
    # Note: <name> must come BEFORE --env flags, otherwise CLI parses incorrectly
    # Note: --scope always passed explicitly — do not rely on Claude CLI's default

    cmd = ["claude", "mcp", "add", "--transport", transport, "--scope", scope]

    # Add server name (must come before --env)
    cmd.append(server_name)

    # Add environment variables if any (must come after name)
    if env_args:
        cmd.extend(env_args)

    # Add static env vars from server config (e.g. ENABLED_TOOLS)
    for key, value in server_info.get("env", {}).items():
        cmd.extend(["--env", f"{key}={value}"])

    # Add separator
    cmd.append("--")

    # Add server command (split into parts)
    cmd.extend(shlex.split(command))

    if dry_run:
        # Mask API keys in dry-run output
        safe_cmd = _mask_secrets_in_args(cmd, api_key)
        click.echo(f"   [DRY RUN] Would run: {' '.join(safe_cmd)}")
        return True

    try:
        # Mask API keys in log output
        safe_command = _mask_secret(command, api_key) if api_key else command
        click.echo(
            f"   Running: claude mcp add --transport {transport} {server_name} -- {safe_command}"
        )
        result = _run_command(cmd, capture_output=True, text=True, timeout=120)

        if result.returncode == 0:
            click.echo(f"   ✅ Successfully installed: {server_name}")
            return True
        else:
            error_msg = result.stderr.strip() if result.stderr else "Unknown error"
            click.echo(f"   ❌ Failed to install {server_name}: {error_msg}", err=True)
            return False

    except subprocess.TimeoutExpired:
        click.echo(f"   ❌ Timeout installing {server_name}", err=True)
        return False
    except Exception as e:
        click.echo(f"   ❌ Error installing {server_name}: {e}", err=True)
        return False


def list_available_servers():
    """List all available MCP servers."""
    click.echo("📋 Available MCP Servers:\n")

    for server_info in MCP_SERVERS.values():
        name = server_info["name"]
        description = server_info["description"]
        api_key_note = ""

        if "api_key_env" in server_info:
            api_key_note = f" (requires {server_info['api_key_env']})"

        # Check if installed
        is_installed = check_mcp_server_installed(name)
        status = "✅ installed" if is_installed else "⬜ not installed"

        click.echo(f"   {name:25} {status}")
        click.echo(f"      {description}{api_key_note}")
        click.echo()

    click.echo(f"Total: {len(MCP_SERVERS)} servers available")


def show_mcp_status():
    """Show MCP server status with fallback info."""
    # Import fallback mappings
    fallbacks = {}
    try:
        from superclaude.hooks.mcp_fallback import MCP_FALLBACKS

        fallbacks = MCP_FALLBACKS
    except ImportError:
        pass

    click.echo("📊 MCP Server Status\n")
    click.echo("┌─────────────────────┬──────────┬─────────────────────┐")
    click.echo("│ Server              │ Status   │ Fallback            │")
    click.echo("├─────────────────────┼──────────┼─────────────────────┤")

    installed_count = 0
    for server_info in MCP_SERVERS.values():
        name = server_info["name"]
        is_installed = check_mcp_server_installed(name)

        if is_installed:
            status = "✅ Active"
            installed_count += 1
        else:
            status = "⬜ —"

        # Get fallback from mapping
        fallback_key = name.lower().replace("-", "")
        # Handle special mappings
        fallback_map = {
            "sequentialthinking": "sequential",
        }
        fallback_key = fallback_map.get(fallback_key, fallback_key)
        fallback = fallbacks.get(fallback_key, "Native")

        click.echo(f"│ {name:19} │ {status:8} │ {fallback:19} │")

    click.echo("└─────────────────────┴──────────┴─────────────────────┘")
    click.echo(f"\n📈 {installed_count}/{len(MCP_SERVERS)} servers active")

    if installed_count < len(MCP_SERVERS):
        click.echo("\n💡 Install with: superclaude mcp --servers <name>")
        click.echo("   Or install all: superclaude mcp --servers all")


def install_mcp_servers(
    selected_servers: Optional[List[str]] = None,
    scope: str = "user",
    dry_run: bool = False,
) -> Tuple[bool, str]:
    """
    Install MCP servers for Claude Code.

    Args:
        selected_servers: List of server names to install, or None for interactive selection
        scope: Installation scope (local, project, user)
        dry_run: If True, only show what would be done

    Returns:
        Tuple of (success, message)
    """
    # Check prerequisites
    success, errors = check_prerequisites()
    if not success:
        error_msg = "Prerequisites not met:\n" + "\n".join(f"  ❌ {e}" for e in errors)
        return False, error_msg

    # Determine which servers to install
    if selected_servers:
        # Use explicitly selected servers
        servers_to_install = []
        for server_name in selected_servers:
            if server_name in MCP_SERVERS:
                servers_to_install.append(server_name)
            else:
                click.echo(f"⚠️  Unknown server: {server_name}", err=True)

        if not servers_to_install:
            return False, "No valid servers selected"
    else:
        # Interactive selection
        click.echo("📋 Available MCP servers:\n")

        server_options = []
        for info in MCP_SERVERS.values():
            api_note = (
                f" (requires {info['api_key_env']})" if "api_key_env" in info else ""
            )
            server_options.append(
                f"{info['name']:25} - {info['description']}{api_note}"
            )

        for i, option in enumerate(server_options, 1):
            click.echo(f"   {i}. {option}")

        click.echo("\n   0. Install all servers")
        click.echo()

        selection = click.prompt(
            "Select servers to install (comma-separated numbers, or 0 for all)",
            default="0",
        )

        if selection.strip() == "0":
            servers_to_install = list(MCP_SERVERS.keys())
        else:
            try:
                indices = [int(x.strip()) for x in selection.split(",")]
                server_list = list(MCP_SERVERS.keys())
                servers_to_install = [
                    server_list[i - 1] for i in indices if 0 < i <= len(server_list)
                ]
            except (ValueError, IndexError):
                return False, "Invalid selection"

    if not servers_to_install:
        return False, "No servers selected"

    # Install each server
    click.echo(f"\n🔌 Installing {len(servers_to_install)} MCP server(s)...\n")

    installed_count = 0
    failed_servers = []

    for server_name in servers_to_install:
        server_info = MCP_SERVERS[server_name]
        if install_mcp_server(server_info, scope, dry_run):
            installed_count += 1
        else:
            failed_servers.append(server_name)

    # Generate result message
    if failed_servers:
        message = f"\n⚠️  Partially completed: {installed_count}/{len(servers_to_install)} servers installed\n"
        message += f"Failed servers: {', '.join(failed_servers)}"
        return False, message
    else:
        message = f"\n✅ Successfully installed {installed_count} MCP server(s)!\n"
        message += "\nℹ️  Use 'claude mcp list' to see all installed servers"
        message += "\nℹ️  Use '/mcp' in Claude Code to check server status"
        return True, message


def uninstall_mcp_servers(
    scope: str = "user",
    project_root: Optional[Path] = None,
    dry_run: bool = False,
) -> Tuple[int, int, int, List[str]]:
    """
    Remove SuperClaude-registered MCP servers from the given scope.

    Only servers in the MCP_SERVERS registry are considered — user-added
    servers at the same scope are left untouched.

    Returns (removed, skipped, failed, messages).
    """
    removed = 0
    skipped = 0
    failed = 0
    messages: List[str] = []

    sc_server_names = list(MCP_SERVERS.keys())

    for server_name in sc_server_names:
        if not check_mcp_server_installed(
            server_name, scope=scope, project_root=project_root
        ):
            skipped += 1
            continue

        if dry_run:
            messages.append(
                f"[DRY-RUN] Would remove MCP server: {server_name} (scope: {scope})"
            )
            removed += 1
            continue

        cmd = ["claude", "mcp", "remove", "--scope", scope, server_name]
        try:
            result = _run_command(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                messages.append(
                    f"✅ Removed MCP server: {server_name} (scope: {scope})"
                )
                removed += 1
            else:
                err = (result.stderr or "").strip() or "unknown error"
                messages.append(f"❌ Failed to remove MCP server {server_name}: {err}")
                failed += 1
        except (
            subprocess.TimeoutExpired,
            subprocess.SubprocessError,
            FileNotFoundError,
        ) as e:
            messages.append(f"❌ Failed to remove MCP server {server_name}: {e}")
            failed += 1

    return removed, skipped, failed, messages
