#!/usr/bin/env python3
"""
dependency-audit.py — Generate a project dependency audit report

Usage:
  python3 dependency-audit.py <project-root>

Extracts dependencies from package.json, requirements.txt, Gemfile, go.mod, etc.,
and presents the Simplicity Coach's 3 questions for each dependency.
"""

import json
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
    with open(filepath) as f:
        data = json.load(f)

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
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and not line.startswith("-"):
                # Separate version specifier
                for sep in ["==", ">=", "<=", "~=", "!="]:
                    if sep in line:
                        name, version = line.split(sep, 1)
                        deps.append({"name": name.strip(), "version": version.strip(), "type": "prod"})
                        break
                else:
                    deps.append({"name": line, "version": "unspecified", "type": "prod"})
    return deps


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
        print(f"## {os.path.basename(filepath)} ({ecosystem})")
        print()

        deps = []
        if "package.json" in filepath:
            deps = parse_package_json(filepath)
        elif "requirements.txt" in filepath:
            deps = parse_requirements_txt(filepath)
        else:
            print(f"  (Parser not implemented — manual review required)")
            print()
            continue

        total_deps += len(deps)

        for dep in deps:
            print(f"### {dep['name']} ({dep['version']}) [{dep['type']}]")
            print()
            print("Simplicity 3 Questions:")
            print(f"  1. How many lines of this library do we actually use?        → [ ]")
            print(f"  2. How long would it take to write those lines ourselves?     → [ ]")
            print(f"  3. Are we confident it will remain safe and compatible in 6m? → [ ]")
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
