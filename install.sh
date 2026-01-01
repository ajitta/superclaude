#!/bin/bash
################################################################################
# SuperClaude Framework Installation Script
################################################################################
#
# This script installs SuperClaude Framework directly from the Git repository.
# It performs the following steps:
#   1. Checks prerequisites (Python 3.10+, UV package manager)
#   2. Installs SuperClaude package in editable mode
#   3. Installs all components to ~/.claude/:
#      - commands/sc/   : 30+ slash commands
#      - agents/        : Agent definitions
#      - skills/        : Skills
#      - hooks/         : Hook scripts (session-init.sh, skill-activator.sh)
#      - settings.json  : Hook configurations merged from hooks/hooks.json
#      - superclaude/   : Core framework (core, modes, mcp, CLAUDE_SC.md)
#   4. Verifies installation
#   5. Provides next steps guidance
#
# Usage:
#   ./install.sh                    # Interactive installation to ~/.claude/
#   ./install.sh --yes              # Non-interactive (auto-yes to prompts)
#   ./install.sh --scope project    # Install to ./.claude/ (current directory)
#   ./install.sh --scope user --force  # Force reinstall to ~/.claude/
#   ./install.sh --target /path/to/project  # Install to specific project directory
#   ./install.sh --help             # Show help message
#
################################################################################

set -e  # Exit on error

# Color codes for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# Installation options
AUTO_YES=false
INSTALL_SCOPE="user"  # user or project
INSTALL_FORCE=false
INSTALL_TARGET=""     # Target directory for installation
INSTALL_EXTRA_ARGS=""

################################################################################
# Helper Functions
################################################################################

print_header() {
    printf "%b\n" "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    printf "%b\n" "${CYAN}$1${NC}"
    printf "%b\n" "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_success() {
    printf "%b\n" "${GREEN}✅ $1${NC}"
}

print_error() {
    printf "%b\n" "${RED}❌ $1${NC}"
}

print_warning() {
    printf "%b\n" "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    printf "%b\n" "${BLUE}ℹ️  $1${NC}"
}

print_step() {
    printf "%b\n" "${CYAN}🔹 $1${NC}"
}

confirm() {
    if [ "$AUTO_YES" = true ]; then
        return 0
    fi

    local prompt="$1"
    local default="${2:-y}"

    if [ "$default" = "y" ]; then
        prompt="$prompt [Y/n]: "
    else
        prompt="$prompt [y/N]: "
    fi

    read -p "$prompt" -r response
    response=${response:-$default}

    if [[ "$response" =~ ^[Yy]$ ]]; then
        return 0
    else
        return 1
    fi
}

################################################################################
# Prerequisite Checks
################################################################################

check_python() {
    print_step "Checking Python installation..."

    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        print_info "Please install Python 3.10 or higher from https://www.python.org/"
        exit 1
    fi

    local python_version=$(python3 --version 2>&1 | awk '{print $2}')
    local major_version=$(echo "$python_version" | cut -d. -f1)
    local minor_version=$(echo "$python_version" | cut -d. -f2)

    if [ "$major_version" -lt 3 ] || ([ "$major_version" -eq 3 ] && [ "$minor_version" -lt 10 ]); then
        print_error "Python $python_version found, but Python 3.10+ is required"
        print_info "Please upgrade Python from https://www.python.org/"
        exit 1
    fi

    print_success "Python $python_version found"
}

check_git() {
    print_step "Checking Git installation..."

    if ! command -v git &> /dev/null; then
        print_warning "Git is not installed"
        print_info "Git is recommended for development. Install from https://git-scm.com/"
    else
        local git_version=$(git --version 2>&1 | awk '{print $3}')
        print_success "Git $git_version found"
    fi
}

check_uv() {
    print_step "Checking UV package manager..."

    if ! command -v uv &> /dev/null; then
        print_warning "UV package manager is not installed"
        return 1
    else
        local uv_version=$(uv --version 2>&1 | awk '{print $2}')
        print_success "UV $uv_version found"
        return 0
    fi
}

install_uv() {
    print_step "Installing UV package manager..."

    if ! confirm "Would you like to install UV now?"; then
        print_error "UV is required for SuperClaude installation"
        print_info "You can install UV manually: curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi

    print_info "Installing UV (this may take a moment)..."
    if curl -LsSf https://astral.sh/uv/install.sh | sh; then
        print_success "UV installed successfully"

        # Add UV to PATH for current session
        export PATH="$HOME/.cargo/bin:$PATH"

        # Verify UV is now available
        if ! command -v uv &> /dev/null; then
            print_warning "UV installed but not in PATH"
            print_info "Please restart your terminal or run: source ~/.bashrc (or ~/.zshrc)"
            print_info "Then run this script again"
            exit 1
        fi
    else
        print_error "Failed to install UV"
        print_info "Please install UV manually: https://github.com/astral-sh/uv"
        exit 1
    fi
}

################################################################################
# Installation Functions
################################################################################

install_package() {
    print_step "Installing SuperClaude package..."

    cd "$PROJECT_ROOT"

    # Check if pyproject.toml exists
    if [ ! -f "pyproject.toml" ]; then
        print_error "pyproject.toml not found in $PROJECT_ROOT"
        print_info "Are you running this script from the SuperClaude repository root?"
        exit 1
    fi

    # Install in editable mode with dev dependencies
    print_info "Running: uv pip install -e \".[dev]\""
    if uv pip install -e ".[dev]"; then
        print_success "SuperClaude package installed successfully"
    else
        print_error "Failed to install SuperClaude package"
        print_info "Try running manually: uv pip install -e \".[dev]\""
        exit 1
    fi
}

install_commands() {
    print_step "Installing SuperClaude components..."

    local target_path
    local effective_scope="$INSTALL_SCOPE"

    # If --target is specified, use project scope in that directory
    if [ -n "$INSTALL_TARGET" ]; then
        target_path="$INSTALL_TARGET/.claude/"
        effective_scope="project"
    elif [ "$INSTALL_SCOPE" = "project" ]; then
        target_path="./.claude/"
    else
        target_path="~/.claude/"
    fi

    print_info "Installing all components to $target_path"
    print_info "  - commands/sc/   : Slash commands"
    print_info "  - agents/        : Agent definitions"
    print_info "  - skills/        : Skills"
    print_info "  - hooks/         : Hook scripts"
    print_info "  - settings.json  : Hook configurations"
    print_info "  - superclaude/   : Core framework (core, modes, mcp)"
    echo ""

    local install_cmd="uv run superclaude install --scope $effective_scope"
    if [ "$INSTALL_FORCE" = true ]; then
        install_cmd="$install_cmd --force"
    fi
    if [ -n "$INSTALL_EXTRA_ARGS" ]; then
        install_cmd="$install_cmd $INSTALL_EXTRA_ARGS"
    fi

    # If --target is specified, run in that directory
    if [ -n "$INSTALL_TARGET" ]; then
        if [ ! -d "$INSTALL_TARGET" ]; then
            print_error "Target directory does not exist: $INSTALL_TARGET"
            exit 1
        fi
        print_info "Running in target directory: $INSTALL_TARGET"
        print_info "Running: (cd $INSTALL_TARGET && $install_cmd)"
        if (cd "$INSTALL_TARGET" && eval "$install_cmd"); then
            print_success "All components installed successfully"
        else
            print_error "Failed to install components"
            print_info "Try running manually: cd $INSTALL_TARGET && $install_cmd"
            exit 1
        fi
    else
        print_info "Running: $install_cmd"
        if eval "$install_cmd"; then
            print_success "All components installed successfully"
        else
            print_error "Failed to install components"
            print_info "Try running manually: $install_cmd"
            exit 1
        fi
    fi
}

verify_installation() {
    print_step "Verifying installation..."

    # Check package version
    local version=$(uv run superclaude --version 2>&1)
    print_info "Installed version: $version"

    # Run doctor command
    print_info "Running health check..."
    if uv run superclaude doctor; then
        print_success "Installation verified successfully"
    else
        print_warning "Health check completed with warnings"
        print_info "You can run 'uv run superclaude doctor' anytime to check status"
    fi

    # List all installed components
    local effective_scope="$INSTALL_SCOPE"
    if [ -n "$INSTALL_TARGET" ]; then
        effective_scope="project"
        print_info "Installed components (target: $INSTALL_TARGET):"
        (cd "$INSTALL_TARGET" && uv run superclaude install --list --scope project)
    else
        print_info "Installed components (scope: $INSTALL_SCOPE):"
        uv run superclaude install --list --scope "$INSTALL_SCOPE"
    fi
}

################################################################################
# Main Installation Flow
################################################################################

show_help() {
    cat << EOF
SuperClaude Framework Installation Script

Usage:
    ./install.sh [OPTIONS]

Options:
    --yes              Non-interactive mode (auto-yes to all prompts)
    --scope SCOPE      Installation scope: user (default) or project
                       - user: Install to ~/.claude/
                       - project: Install to ./.claude/
    --target PATH      Install to specific project directory
                       - Installs to PATH/.claude/
                       - Automatically uses project scope
    --force            Force reinstall if components already exist
    --help             Show this help message

Description:
    Installs SuperClaude Framework directly from the Git repository.
    Performs installation in editable/development mode with all features.

Requirements:
    - Python 3.10 or higher
    - UV package manager (will be installed if missing)

Examples:
    ./install.sh                      # Interactive installation to ~/.claude/
    ./install.sh --yes                # Non-interactive installation
    ./install.sh --scope project      # Install to ./.claude/ (current directory)
    ./install.sh --scope user --force # Force reinstall to ~/.claude/
    ./install.sh --yes --scope project # Non-interactive project installation
    ./install.sh --target /path/to/myproject  # Install to specific directory
    ./install.sh --target ~/projects/myapp --force  # Force install to target

For more information:
    https://github.com/SuperClaude-Org/SuperClaude_Framework
EOF
    exit 0
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --yes|-y)
                AUTO_YES=true
                shift
                ;;
            --scope)
                if [ -z "$2" ] || [[ "$2" =~ ^- ]]; then
                    print_error "--scope requires a value (user or project)"
                    exit 1
                fi
                if [ "$2" != "user" ] && [ "$2" != "project" ]; then
                    print_error "Invalid scope: $2. Must be 'user' or 'project'"
                    exit 1
                fi
                INSTALL_SCOPE="$2"
                shift 2
                ;;
            --target)
                if [ -z "$2" ] || [[ "$2" =~ ^- ]]; then
                    print_error "--target requires a directory path"
                    exit 1
                fi
                INSTALL_TARGET="$2"
                shift 2
                ;;
            --force)
                INSTALL_FORCE=true
                shift
                ;;
            --help|-h)
                show_help
                ;;
            *)
                # Pass unknown arguments to superclaude install command
                INSTALL_EXTRA_ARGS="$INSTALL_EXTRA_ARGS $1"
                shift
                ;;
        esac
    done
}

main() {
    # Parse command line arguments
    parse_args "$@"

    # Print header
    clear
    print_header "🚀 SuperClaude Framework Installation"
    echo ""
    print_info "This script will install SuperClaude Framework in development mode"
    print_info "Installation location: $PROJECT_ROOT"
    if [ -n "$INSTALL_TARGET" ]; then
        print_info "Target directory: $INSTALL_TARGET/.claude/"
    elif [ "$INSTALL_SCOPE" = "project" ]; then
        print_info "Target scope: project (./.claude/)"
    else
        print_info "Target scope: user (~/.claude/)"
    fi
    if [ "$INSTALL_FORCE" = true ]; then
        print_info "Force mode: enabled (will reinstall existing components)"
    fi
    echo ""

    if [ "$AUTO_YES" != true ]; then
        if ! confirm "Continue with installation?"; then
            print_info "Installation cancelled"
            exit 0
        fi
        echo ""
    fi

    # Phase 1: Check prerequisites
    print_header "📋 Phase 1: Checking Prerequisites"
    check_python
    check_git
    if ! check_uv; then
        install_uv
    fi
    echo ""

    # Phase 2: Install package
    print_header "📦 Phase 2: Installing SuperClaude Package"
    install_package
    echo ""

    # Phase 3: Install all components
    print_header "⚙️  Phase 3: Installing All Components"
    install_commands
    echo ""

    # Phase 4: Verify installation
    print_header "✅ Phase 4: Verifying Installation"
    verify_installation
    echo ""

    # Phase 5: Next steps
    print_header "🎉 Installation Complete!"
    echo ""
    print_success "SuperClaude Framework is now installed!"
    echo ""
    print_info "Next Steps:"
    echo "  1. Run health check:        uv run superclaude doctor"
    echo "  2. View all components:     uv run superclaude install --list"
    echo "  3. Try a command:           /sc:help"
    echo ""
    local target_base
    if [ -n "$INSTALL_TARGET" ]; then
        target_base="$INSTALL_TARGET/.claude"
    elif [ "$INSTALL_SCOPE" = "project" ]; then
        target_base="./.claude"
    else
        target_base="~/.claude"
    fi

    print_info "Installed locations:"
    echo "  • Commands:     $target_base/commands/sc/"
    echo "  • Agents:       $target_base/agents/"
    echo "  • Skills:       $target_base/skills/"
    echo "  • Hook scripts: $target_base/hooks/"
    echo "  • Hook config:  $target_base/settings.json"
    echo "  • Framework:    $target_base/superclaude/"
    echo ""
    print_info "Optional - Install MCP Servers for enhanced features:"
    echo "  • List available servers:   uv run superclaude mcp --list"
    echo "  • Interactive installation: uv run superclaude mcp"
    echo "  • Specific servers:         uv run superclaude mcp --servers tavily context7"
    echo ""
    print_info "Documentation:"
    echo "  • Quick Start:  docs/getting-started/quick-start.md"
    echo "  • User Guide:   docs/user-guide/"
    echo "  • Commands:     docs/reference/commands-list.md"
    echo ""
    print_success "Happy coding with SuperClaude! 🚀"
    echo ""
}

# Run main function
main "$@"
