#!/usr/bin/env python3
"""
dependency-audit.py — Generate a project dependency audit report

Usage:
  python3 dependency-audit.py <project-root>

Extracts dependencies from package.json, requirements.txt, pyproject.toml, Pipfile,
and presents the Simplicity Coach's 3 questions for each dependency.
"""

import json
import re
import sys
import os
from pathlib import Path


def find_dependency_files(root: str) -> dict:
    """Find dependency management files in the project root."""
    root_path = Path(root)
    found = {}

    patterns = {
        "package.json": "npm/node",
        "requirements.txt": "pip/python",
        "Pipfile": "pipenv/python",
        "pyproject.toml": "python",
        "Gemfile": "bundler/ruby",
        "go.mod": "go",
        "Cargo.toml": "cargo/rust",
        "build.gradle": "gradle/java",
        "pom.xml": "maven/java",
    }

    for filename, ecosystem in patterns.items():
        filepath = root_path / filename
        if filepath.exists():
            found[str(filepath)] = ecosystem

    return found


def parse_package_json(filepath: str) -> list:
    """Extract direct dependencies from package.json."""
    try:
        with open(filepath) as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"  Warning: Could not parse {filepath}: {e}")
        return []

    deps = []
    for section in ["dependencies", "devDependencies"]:
        if section in data:
            for name, version in data[section].items():
                deps.append({
                    "name": name,
                    "version": version,
                    "type": "dev" if section == "devDependencies" else "prod",
                })
    return deps


def parse_requirements_txt(filepath: str) -> list:
    """Extract dependencies from requirements.txt."""
    deps = []
    try:
        with open(filepath) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and not line.startswith("-"):
                    for sep in ["==", ">=", "<=", "~=", "!="]:
                        if sep in line:
                            name, version = line.split(sep, 1)
                            deps.append({"name": name.strip(), "version": version.strip(), "type": "prod"})
                            break
                    else:
                        deps.append({"name": line, "version": "unspecified", "type": "prod"})
    except OSError as e:
        print(f"  Warning: Could not read {filepath}: {e}")
    return deps


def parse_pyproject_toml(filepath: str) -> list:
    """Extract dependencies from pyproject.toml using regex (no toml dependency needed)."""
    deps = []
    try:
        content = Path(filepath).read_text()
    except OSError as e:
        print(f"  Warning: Could not read {filepath}: {e}")
        return []

    # Match [project] dependencies array
    dep_match = re.search(r'\[project\].*?dependencies\s*=\s*\[(.*?)\]', content, re.DOTALL)
    if dep_match:
        dep_block = dep_match.group(1)
        for item in re.findall(r'"([^"]+)"', dep_block):
            # Parse "name>=version" or "name[extra]>=version"
            m = re.match(r'([a-zA-Z0-9_.-]+)(?:\[.*?\])?\s*([><=!~]+)?\s*(.*)?', item)
            if m:
                name = m.group(1)
                version = (m.group(3) or "unspecified").strip().rstrip('"').rstrip(",")
                deps.append({"name": name, "version": version, "type": "prod"})

    # Match [project.optional-dependencies] sections
    for section_match in re.finditer(
        r'\[project\.optional-dependencies\]\s*\n(.*?)(?=\n\[|\Z)', content, re.DOTALL
    ):
        section = section_match.group(1)
        for group_match in re.finditer(r'(\w+)\s*=\s*\[(.*?)\]', section, re.DOTALL):
            group_name = group_match.group(1)
            for item in re.findall(r'"([^"]+)"', group_match.group(2)):
                m = re.match(r'([a-zA-Z0-9_.-]+)(?:\[.*?\])?\s*([><=!~]+)?\s*(.*)?', item)
                if m:
                    name = m.group(1)
                    version = (m.group(3) or "unspecified").strip().rstrip('"').rstrip(",")
                    deps.append({"name": name, "version": version, "type": f"optional ({group_name})"})

    return deps


def parse_pipfile(filepath: str) -> list:
    """Extract dependencies from Pipfile using regex (no toml dependency needed)."""
    deps = []
    try:
        content = Path(filepath).read_text()
    except OSError as e:
        print(f"  Warning: Could not read {filepath}: {e}")
        return []

    for section, dep_type in [("[packages]", "prod"), ("[dev-packages]", "dev")]:
        match = re.search(
            rf'\{re.escape(section)}\]\s*\n(.*?)(?=\n\[|\Z)', content, re.DOTALL
        )
        if match:
            for line in match.group(1).strip().splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    parts = line.split("=", 1)
                    if len(parts) == 2:
                        name = parts[0].strip()
                        version = parts[1].strip().strip('"').strip("'")
                        if version == "*":
                            version = "any"
                        deps.append({"name": name, "version": version, "type": dep_type})

    return deps


PARSERS = {
    "package.json": parse_package_json,
    "requirements.txt": parse_requirements_txt,
    "pyproject.toml": parse_pyproject_toml,
    "Pipfile": parse_pipfile,
}


def generate_report(root: str):
    """Generate a dependency audit report."""
    dep_files = find_dependency_files(root)

    if not dep_files:
        print(f"No dependency management files found in: {root}")
        return

    print("# Dependency Audit Report")
    print(f"\nProject: {os.path.basename(os.path.abspath(root))}")
    print(f"Path: {os.path.abspath(root)}")
    print()

    total_deps = 0

    for filepath, ecosystem in dep_files.items():
        basename = os.path.basename(filepath)
        print(f"## {basename} ({ecosystem})")
        print()

        parser = PARSERS.get(basename)
        if parser:
            deps = parser(filepath)
        else:
            print(f"  (No parser available — manual review required)")
            print()
            continue

        total_deps += len(deps)

        if not deps:
            print("  No dependencies found.")
            print()
            continue

        for dep in deps:
            print(f"### {dep['name']} ({dep['version']}) [{dep['type']}]")
            print()
            print("Simplicity 3 Questions:")
            print(f"  1. How many lines of this library do we actually use?        -> [ ]")
            print(f"  2. How long would it take to write those lines ourselves?     -> [ ]")
            print(f"  3. Are we confident it will remain safe and compatible in 6m? -> [ ]")
            print()

    print("---")
    print(f"\nTotal direct dependencies: {total_deps}")
    print("\nAnswer the 3 questions for each dependency.")
    print("Consider removing any dependency where all 3 answers are uncertain.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 dependency-audit.py <project-root>")
        sys.exit(1)

    generate_report(sys.argv[1])
