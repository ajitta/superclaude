"""
MCP Server Installation Module for SuperClaude

Installs and manages MCP servers using the latest Claude Code API.
Based on the installer logic from commit d4a17fc but adapted for modern Claude Code.
"""

import os
import platform
import shlex
import subprocess
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
    "magic": {
        "name": "magic",
        "description": "Modern UI component generation and design systems",
        "transport": "stdio",
        "command": "npx -y @21st-dev/magic",
        "required": False,
        "api_key_env": "TWENTYFIRST_API_KEY",
        "api_key_description": "21st.dev API key for UI component generation",
    },
    "playwright": {
        "name": "playwright",
        "description": "Cross-browser E2E testing and automation",
        "transport": "stdio",
        "command": "npx -y @playwright/mcp@latest",
        "required": False,
    },
    "serena": {
        "name": "serena",
        "description": "Semantic code analysis and intelligent editing",
        "transport": "stdio",
        "command": "uvx --from git+https://github.com/oraios/serena serena start-mcp-server --context claude-code --enable-web-dashboard false --enable-gui-log-window false",
        "required": False,
    },
    "filesystem-with-morph": {
        "name": "filesystem-with-morph",
        "description": "Pattern-based bulk code transformations with filesystem access",
        "transport": "stdio",
        "command": "npx -y @morphllm/morphmcp",
        "required": False,
        "api_key_env": "MORPH_API_KEY",
        "api_key_description": "Morph API key for code transformations",
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
    "chrome-devtools": {
        "name": "chrome-devtools",
        "description": "Performance analysis and Core Web Vitals (CLS, LCP, memory profiling). Use --perf or --devtools flag.",
        "transport": "stdio",
        "command": "npx -y chrome-devtools-mcp@latest",
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

    return len(errors) == 0, errors


def check_mcp_server_installed(server_name: str) -> bool:
    """Check if an MCP server is already installed."""
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

    # Check if already installed
    if check_mcp_server_installed(server_name):
        click.echo(f"   ✅ Already installed: {server_name}")
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
    # Format: claude mcp add --transport <transport> [--scope <scope>] <name> [--env KEY=VALUE] -- <command>
    # Note: <name> must come BEFORE --env flags, otherwise CLI parses incorrectly

    cmd = ["claude", "mcp", "add", "--transport", transport]

    # Add scope if not default
    if scope != "local":
        cmd.extend(["--scope", scope])

    # Add server name (must come before --env)
    cmd.append(server_name)

    # Add environment variables if any (must come after name)
    if env_args:
        cmd.extend(env_args)

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
            "filesystemwithmorph": "morphllm",
            "chromedevtools": "devtools",
            "airisagent": "airis-agent",
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
