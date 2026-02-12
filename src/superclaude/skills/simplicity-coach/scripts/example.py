#!/usr/bin/env python3
"""
dependency-audit.py — 프로젝트 의존성 감사 보고서 생성

사용법:
  python3 dependency-audit.py <project-root>

package.json, requirements.txt, Gemfile, go.mod 등에서 의존성을 추출하고,
각 의존성에 대해 Simplicity Coach의 3가지 질문을 제시한다.
"""

import json
import sys
import os
from pathlib import Path


def find_dependency_files(root: str) -> dict:
    """프로젝트 루트에서 의존성 관리 파일을 찾는다."""
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
    """package.json에서 직접 의존성을 추출한다."""
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
    """requirements.txt에서 의존성을 추출한다."""
    deps = []
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and not line.startswith("-"):
                # 버전 지정 분리
                for sep in ["==", ">=", "<=", "~=", "!="]:
                    if sep in line:
                        name, version = line.split(sep, 1)
                        deps.append({"name": name.strip(), "version": version.strip(), "type": "prod"})
                        break
                else:
                    deps.append({"name": line, "version": "unspecified", "type": "prod"})
    return deps


def generate_report(root: str):
    """의존성 감사 보고서를 생성한다."""
    dep_files = find_dependency_files(root)

    if not dep_files:
        print(f"의존성 관리 파일을 찾을 수 없습니다: {root}")
        return

    print("# 의존성 감사 보고서")
    print(f"\n프로젝트: {os.path.basename(os.path.abspath(root))}")
    print(f"경로: {os.path.abspath(root)}")
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
            print(f"  (파서 미구현 — 수동 확인 필요)")
            print()
            continue

        total_deps += len(deps)

        for dep in deps:
            print(f"### {dep['name']} ({dep['version']}) [{dep['type']}]")
            print()
            print("Simplicity 3가지 질문:")
            print(f"  1. 이 라이브러리에서 실제로 사용하는 기능이 몇 줄인가?  → [ ]")
            print(f"  2. 그 몇 줄을 직접 작성하면 얼마나 걸리는가?           → [ ]")
            print(f"  3. 6개월 후에도 안전하고 호환될 것이라 확신하는가?      → [ ]")
            print()

    print("---")
    print(f"\n총 직접 의존성: {total_deps}개")
    print("\n각 의존성에 대해 3가지 질문에 답해보세요.")
    print("3개 모두 불확실한 의존성은 제거를 고려하세요.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python3 dependency-audit.py <project-root>")
        sys.exit(1)

    generate_report(sys.argv[1])
