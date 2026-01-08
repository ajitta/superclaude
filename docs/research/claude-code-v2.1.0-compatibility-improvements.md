# Claude Code v2.1.0 호환성 개선 방안

> **문서 버전**: 1.0.0
> **작성일**: 2026-01-08
> **분석 대상**: Claude Code v2.1.0 릴리즈 노트
> **적용 대상**: SuperClaude v4.2.1+ajitta

---

## 1. 개요

### 1.1 배경

Claude Code v2.1.0에서 스킬 시스템, 훅 시스템, 에이전트 관리에 대한 주요 기능이 추가되었습니다.
SuperClaude가 이러한 새로운 기능과 호환되도록 개선이 필요합니다.

### 1.2 분석 범위

- **스킬 프론트매터 스키마**: 새로운 필드 6개
- **훅 시스템**: JSON 스키마 확장 + 인라인 훅
- **CLI 인스톨러**: 핫리로드 + 설정 스키마
- **에이전트 관리**: Task(AgentName) 비활성화 구문

### 1.3 우선순위 분류

| 우선순위 | 설명 | 항목 수 |
|---------|------|--------|
| 🔴 HIGH | 즉시 구현 필요 (호환성 필수) | 6개 |
| 🟡 MEDIUM | 기능 향상 (권장) | 4개 |
| 🟢 LOW | 편의 기능 (선택) | 3개 |

---

## 2. 🔴 HIGH PRIORITY: 프론트매터 스키마 개선

### 2.1 `context: fork` - 서브에이전트 컨텍스트 실행

#### 현재 상태
- SuperClaude 스킬은 메인 에이전트 컨텍스트에서만 실행
- 격리된 실행 환경 미지원

#### v2.1.0 기능
```yaml
---
name: my-skill
context: fork  # 스킬이 분리된 서브에이전트에서 실행
---
```

#### 구현 방안

**영향 파일**:
- `src/superclaude/skills/*/SKILL.md` - 프론트매터 필드 추가
- `src/superclaude/scripts/skill_activator.py` - context 파싱 로직

**구현 코드**:
```python
# skill_activator.py 수정
def parse_skill_frontmatter(skill_path: Path) -> dict:
    """스킬 프론트매터 파싱"""
    content = skill_path.read_text()
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if match:
        import yaml
        frontmatter = yaml.safe_load(match.group(1))
        return frontmatter
    return {}

def should_fork_context(skill_path: Path) -> bool:
    """context: fork 여부 확인"""
    fm = parse_skill_frontmatter(skill_path)
    return fm.get('context', 'inline') == 'fork'
```

**적용 예시**:
```yaml
# src/superclaude/skills/confidence-check/SKILL.md
---
name: confidence-check
description: Pre-implementation confidence assessment
context: fork  # 격리된 서브에이전트에서 실행
---
```

#### 효과
- 스킬 실행 중 메인 컨텍스트 오염 방지
- 병렬 스킬 실행 가능
- 에러 격리

---

### 2.2 `agent` 필드 - 에이전트 타입 지정

#### 현재 상태
- 스킬 실행 시 에이전트 타입 지정 불가
- 모든 스킬이 동일한 실행 컨텍스트 사용

#### v2.1.0 기능
```yaml
---
name: security-scan
agent: security-engineer  # 특정 에이전트로 실행
---
```

#### 구현 방안

**영향 파일**:
- `src/superclaude/skills/*/SKILL.md` - agent 필드 추가
- `src/superclaude/agents/*.md` - 에이전트 정의 참조

**프론트매터 스키마**:
```yaml
---
name: skill-name
description: Skill description
agent: backend-architect  # 선택적: 실행할 에이전트 타입
# 유효 값: system-architect, backend-architect, frontend-architect,
#          security-engineer, quality-engineer, devops-architect,
#          pm-agent, performance-engineer, refactoring-expert,
#          root-cause-analyst, python-expert
---
```

**라우팅 로직**:
```python
# skill_activator.py 추가
VALID_AGENTS = {
    'system-architect', 'backend-architect', 'frontend-architect',
    'security-engineer', 'quality-engineer', 'devops-architect',
    'pm-agent', 'performance-engineer', 'refactoring-expert',
    'root-cause-analyst', 'python-expert'
}

def get_agent_for_skill(skill_path: Path) -> str | None:
    """스킬에 지정된 에이전트 타입 반환"""
    fm = parse_skill_frontmatter(skill_path)
    agent = fm.get('agent')
    if agent and agent in VALID_AGENTS:
        return agent
    return None
```

**적용 예시**:
```yaml
# 보안 스캔 스킬 → security-engineer 에이전트 사용
---
name: security-scan
agent: security-engineer
---

# 성능 분석 스킬 → performance-engineer 에이전트 사용
---
name: perf-analyze
agent: performance-engineer
---
```

#### 효과
- 스킬별 전문화된 에이전트 활용
- 도메인 특화 분석 품질 향상
- 에이전트 역량 최적화

---

### 2.3 프론트매터 `hooks` - 인라인 훅 정의

#### 현재 상태
- 훅은 `src/superclaude/hooks/hooks.json`에서만 정의
- 스킬/에이전트별 훅 스코핑 불가

#### v2.1.0 기능
```yaml
---
name: my-skill
hooks:
  PreToolUse:
    - type: command
      command: python validate.py
  PostToolUse:
    - type: command
      command: python cleanup.py
  Stop:
    - type: command
      command: python finalize.py
---
```

#### 구현 방안

**영향 파일**:
- `src/superclaude/skills/*/SKILL.md` - hooks 필드
- `src/superclaude/agents/*.md` - hooks 필드
- `src/superclaude/commands/*.md` - hooks 필드

**훅 스키마 정의**:
```yaml
hooks:
  PreToolUse:            # 도구 사용 전
    - type: command      # command | prompt
      command: string    # 실행할 명령어
      matcher: string    # 도구 매처 (선택)
      timeout: number    # 타임아웃 ms (선택)
      once: boolean      # 세션당 1회만 (선택)
  PostToolUse:           # 도구 사용 후
    - type: command
      command: string
      matcher: string
  Stop:                  # 스킬/에이전트 종료 시
    - type: command
      command: string
```

**파싱 코드**:
```python
# hooks/inline_hooks.py (신규)
from dataclasses import dataclass
from typing import Literal

@dataclass
class InlineHook:
    type: Literal['command', 'prompt']
    command: str
    matcher: str | None = None
    timeout: int = 30
    once: bool = False

def parse_inline_hooks(frontmatter: dict) -> dict[str, list[InlineHook]]:
    """프론트매터에서 인라인 훅 파싱"""
    hooks_data = frontmatter.get('hooks', {})
    result = {}

    for hook_type in ['PreToolUse', 'PostToolUse', 'Stop']:
        if hook_type in hooks_data:
            result[hook_type] = [
                InlineHook(**h) for h in hooks_data[hook_type]
            ]
    return result
```

**적용 예시**:
```yaml
# src/superclaude/skills/confidence-check/SKILL.md
---
name: confidence-check
hooks:
  PreToolUse:
    - type: command
      command: python {{SCRIPTS_PATH}}/validate_context.py
      matcher: WebFetch|WebSearch
      once: true
  Stop:
    - type: command
      command: python {{SCRIPTS_PATH}}/log_confidence_result.py
---
```

#### 효과
- 스킬/에이전트별 훅 스코핑
- hooks.json 분리 관리 불필요
- 훅과 스킬 정의 공존으로 가독성 향상

---

### 2.4 `once: true` - 세션당 1회 실행

#### 현재 상태
- 모든 훅은 조건 충족 시 매번 실행
- 세션 범위 실행 제어 없음

#### v2.1.0 기능
```yaml
hooks:
  PreToolUse:
    - type: command
      command: python init.py
      once: true  # 세션에서 최초 1회만 실행
```

#### 구현 방안

**영향 파일**:
- `src/superclaude/hooks/hooks.json` - once 필드
- `src/superclaude/scripts/session_init.py` - 실행 기록 관리

**hooks.json 스키마 확장**:
```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python init.py",
            "timeout": 10,
            "once": true  // 신규 필드
          }
        ]
      }
    ]
  }
}
```

**세션 추적 구현**:
```python
# scripts/hook_tracker.py (신규)
import json
from pathlib import Path
from datetime import datetime

HOOK_EXECUTION_LOG = Path.home() / '.claude' / '.hook_executions.json'

def has_executed_once(hook_id: str, session_id: str) -> bool:
    """훅이 현재 세션에서 실행되었는지 확인"""
    if not HOOK_EXECUTION_LOG.exists():
        return False

    data = json.loads(HOOK_EXECUTION_LOG.read_text())
    return data.get(session_id, {}).get(hook_id, False)

def mark_executed(hook_id: str, session_id: str):
    """훅 실행 기록"""
    data = {}
    if HOOK_EXECUTION_LOG.exists():
        data = json.loads(HOOK_EXECUTION_LOG.read_text())

    if session_id not in data:
        data[session_id] = {}
    data[session_id][hook_id] = datetime.now().isoformat()

    HOOK_EXECUTION_LOG.write_text(json.dumps(data, indent=2))
```

#### 효과
- 초기화 훅 중복 실행 방지
- 세션 범위 일회성 작업 지원
- 리소스 효율성 향상

---

### 2.5 `allowed-tools` YAML 스타일

#### 현재 상태
- 도구 허용 목록 명시적 선언 없음
- 암묵적으로 모든 도구 사용 가능

#### v2.1.0 기능
```yaml
---
name: my-skill
allowed-tools:
  - Read
  - Grep
  - WebFetch
  - Task(backend-architect)
---
```

#### 구현 방안

**영향 파일**:
- `src/superclaude/skills/*/SKILL.md`
- `src/superclaude/commands/*.md`

**스키마 정의**:
```yaml
allowed-tools:
  # 기본 도구
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash

  # 네트워크 도구
  - WebFetch
  - WebSearch

  # 에이전트 도구
  - Task(backend-architect)
  - Task(security-engineer)

  # MCP 도구
  - mcp__context7__*
  - mcp__tavily__*
  - mcp__serena__*
```

**파싱 및 검증**:
```python
# tools/allowed_tools.py (신규)
import re

def parse_allowed_tools(frontmatter: dict) -> list[str]:
    """허용 도구 목록 파싱"""
    return frontmatter.get('allowed-tools', [])

def is_tool_allowed(tool_name: str, allowed: list[str]) -> bool:
    """도구 사용 허용 여부 확인"""
    if not allowed:  # 빈 목록 = 모든 도구 허용
        return True

    for pattern in allowed:
        if pattern.endswith('*'):
            # 와일드카드 패턴 (예: mcp__serena__*)
            if tool_name.startswith(pattern[:-1]):
                return True
        elif pattern.startswith('Task('):
            # 에이전트 패턴 (예: Task(backend-architect))
            if tool_name == 'Task' and pattern[5:-1] in tool_name:
                return True
        elif tool_name == pattern:
            return True
    return False
```

**적용 예시**:
```yaml
# src/superclaude/skills/confidence-check/SKILL.md
---
name: confidence-check
allowed-tools:
  - Read
  - Grep
  - Glob
  - WebFetch
  - WebSearch
  - mcp__context7__*
  - mcp__tavily__*
  - mcp__serena__find_symbol
  - mcp__serena__search_for_pattern
---
```

#### 효과
- 스킬별 도구 사용 범위 명시적 제한
- 보안 강화 (불필요한 도구 접근 차단)
- 문서화 역할 (스킬이 사용하는 도구 명확화)

---

### 2.6 `user-invocable` - 슬래시 메뉴 가시성

#### 현재 상태
- 모든 스킬이 슬래시 명령 메뉴에 표시
- 내부 전용 스킬 숨김 불가

#### v2.1.0 기능
```yaml
---
name: internal-utility
user-invocable: false  # 슬래시 메뉴에서 숨김
---
```

#### 구현 방안

**영향 파일**:
- `src/superclaude/skills/*/SKILL.md`
- `src/superclaude/cli/install_skill.py` - 목록 필터링

**스키마**:
```yaml
---
name: skill-name
user-invocable: true   # 기본값: true (메뉴에 표시)
                       # false: 메뉴에서 숨김, 프로그래매틱 호출만 가능
---
```

**필터링 로직**:
```python
# cli/install_skill.py 수정
def list_user_invocable_skills() -> list[str]:
    """사용자 호출 가능한 스킬만 반환"""
    all_skills = list_available_skills()
    invocable = []

    for skill_name in all_skills:
        skill_path = _get_skill_source(skill_name)
        if skill_path:
            fm = parse_skill_frontmatter(skill_path / 'SKILL.md')
            if fm.get('user-invocable', True):  # 기본값 True
                invocable.append(skill_name)

    return invocable
```

**적용 예시**:
```yaml
# 내부 유틸리티 스킬 (메뉴에서 숨김)
---
name: tavily-response-filter
user-invocable: false
---

# 사용자용 스킬 (메뉴에 표시)
---
name: confidence-check
user-invocable: true
---
```

#### 효과
- 슬래시 메뉴 정리 (필요한 스킬만 표시)
- 내부/유틸리티 스킬 분리
- 사용자 경험 개선

---

## 3. 🟡 MEDIUM PRIORITY: CLI/인스톨러 개선

### 3.1 스킬 핫리로드

#### 현재 상태
- 스킬 수정 후 재설치 필요
- `superclaude install-skill` 명령 재실행 필요

#### v2.1.0 기능
- `~/.claude/skills/` 또는 `.claude/skills/` 디렉토리의 스킬 자동 감지
- 파일 수정 시 즉시 반영

#### 구현 방안

**파일 감시 구현**:
```python
# cli/skill_watcher.py (신규)
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path

class SkillReloadHandler(FileSystemEventHandler):
    def __init__(self, skill_dirs: list[Path]):
        self.skill_dirs = skill_dirs

    def on_modified(self, event):
        if event.src_path.endswith('.md'):
            print(f"[SuperClaude] Skill reloaded: {event.src_path}")
            # 스킬 캐시 무효화
            invalidate_skill_cache(Path(event.src_path).parent.name)

    def on_created(self, event):
        if event.is_directory:
            print(f"[SuperClaude] New skill detected: {event.src_path}")

def start_skill_watcher():
    """스킬 디렉토리 감시 시작"""
    skill_dirs = [
        Path.home() / '.claude' / 'skills',
        Path.cwd() / '.claude' / 'skills',
    ]

    observer = Observer()
    for dir in skill_dirs:
        if dir.exists():
            observer.schedule(SkillReloadHandler(skill_dirs), str(dir), recursive=True)

    observer.start()
    return observer
```

**의존성 추가**:
```toml
# pyproject.toml
[project.optional-dependencies]
dev = [
    "watchdog>=3.0.0",  # 파일 시스템 감시
]
```

#### 효과
- 개발 생산성 향상
- 스킬 테스트 사이클 단축
- Claude Code 네이티브 동작과 일치

---

### 3.2 Task(AgentName) 비활성화 구문

#### 현재 상태
- 에이전트 비활성화 설정 없음
- 모든 에이전트 항상 사용 가능

#### v2.1.0 기능
- `settings.json`에서 특정 에이전트 비활성화:
```json
{
  "permissions": {
    "deny": ["Task(security-engineer)", "Task(devops-architect)"]
  }
}
```

#### 구현 방안

**설정 스키마 확장**:
```json
// .claude/settings.json
{
  "superclaude": {
    "agents": {
      "disabled": [
        "security-engineer",
        "devops-architect"
      ]
    }
  }
}
```

**CLI 설정 명령 추가**:
```python
# cli/main.py 확장
@click.command()
@click.option('--disable-agent', multiple=True, help='Disable specific agent')
@click.option('--enable-agent', multiple=True, help='Enable specific agent')
def agents(disable_agent, enable_agent):
    """Manage agent availability"""
    settings = load_settings()

    for agent in disable_agent:
        if agent not in settings['superclaude']['agents']['disabled']:
            settings['superclaude']['agents']['disabled'].append(agent)

    for agent in enable_agent:
        if agent in settings['superclaude']['agents']['disabled']:
            settings['superclaude']['agents']['disabled'].remove(agent)

    save_settings(settings)
```

#### 효과
- 프로젝트별 에이전트 제어
- 불필요한 에이전트 호출 방지
- 보안/컴플라이언스 요구사항 충족

---

### 3.3 스킬 컨텍스트 카테고리

#### 현재 상태
- `/context` 명령에서 스킬이 별도 카테고리로 분류되지 않음

#### v2.1.0 기능
- 스킬이 독립 카테고리로 컨텍스트 시각화에 표시

#### 구현 방안

**context_loader.py 수정**:
```python
# scripts/context_loader.py
def get_context_visualization() -> dict:
    """컨텍스트 시각화 데이터 생성"""
    return {
        'files': get_loaded_files(),
        'agents': get_active_agents(),
        'skills': get_loaded_skills(),  # 신규 카테고리
        'mcp': get_mcp_servers(),
    }

def get_loaded_skills() -> list[dict]:
    """로드된 스킬 정보 반환"""
    skill_dirs = [
        Path.home() / '.claude' / 'skills',
        Path.cwd() / '.claude' / 'skills',
    ]

    skills = []
    for base in skill_dirs:
        if not base.exists():
            continue
        for skill_dir in base.iterdir():
            if skill_dir.is_dir():
                manifest = skill_dir / 'SKILL.md'
                if manifest.exists():
                    fm = parse_skill_frontmatter(manifest)
                    skills.append({
                        'name': fm.get('name', skill_dir.name),
                        'description': fm.get('description', ''),
                        'tokens': estimate_skill_tokens(manifest),
                    })
    return skills
```

#### 효과
- 컨텍스트 사용량 가시성 향상
- 스킬 토큰 비용 추적
- 디버깅 용이성

---

### 3.4 스킬 토큰 추정

#### 현재 상태
- 스킬 토큰 비용 추정 없음

#### v2.1.0 기능
- 프론트매터만 로드하여 정확한 토큰 추정
- `/context`에서 스킬별 토큰 사용량 표시

#### 구현 방안

```python
# scripts/token_estimator.py (신규)
def estimate_skill_tokens(skill_path: Path) -> int:
    """스킬 토큰 사용량 추정 (프론트매터 기준)"""
    content = skill_path.read_text()

    # 프론트매터만 추출
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if match:
        frontmatter = match.group(1)
        # 대략적인 토큰 추정 (4자 = 1토큰)
        return len(frontmatter) // 4

    return 0

def estimate_full_skill_tokens(skill_dir: Path) -> int:
    """스킬 전체 토큰 사용량 추정"""
    total = 0
    for file in skill_dir.glob('**/*'):
        if file.is_file() and file.suffix in {'.md', '.ts', '.py'}:
            total += len(file.read_text()) // 4
    return total
```

#### 효과
- 컨텍스트 예산 관리
- 스킬 최적화 가이드라인 제공
- 토큰 효율성 분석

---

## 4. 🟢 LOW PRIORITY: 편의 기능

### 4.1 language 설정

```yaml
# .claude/settings.json
{
  "language": "korean"  # Claude 응답 언어
}
```

### 4.2 respectGitignore

```yaml
# .claude/settings.json
{
  "respectGitignore": true  # @-멘션 파일 피커에서 gitignore 적용
}
```

### 4.3 MCP list_changed 알림

- MCP 서버가 도구 목록 변경 시 동적 업데이트
- 재연결 없이 새 도구 사용 가능

---

## 5. 구현 로드맵

### Phase 1: 프론트매터 스키마 (1주)

| 작업 | 파일 | 우선순위 |
|------|------|---------|
| context 필드 추가 | skills/*.md | 🔴 |
| agent 필드 추가 | skills/*.md | 🔴 |
| hooks 인라인 지원 | skills/*.md, agents/*.md | 🔴 |
| once 필드 추가 | hooks/hooks.json | 🔴 |
| allowed-tools 필드 | skills/*.md, commands/*.md | 🔴 |
| user-invocable 필드 | skills/*.md | 🔴 |

### Phase 2: 훅 시스템 (1주)

| 작업 | 파일 | 우선순위 |
|------|------|---------|
| 인라인 훅 파서 | hooks/inline_hooks.py | 🔴 |
| 세션 훅 추적기 | scripts/hook_tracker.py | 🔴 |
| hooks.json 스키마 | hooks/hooks.json | 🟡 |

### Phase 3: CLI 개선 (2주)

| 작업 | 파일 | 우선순위 |
|------|------|---------|
| 스킬 핫리로드 | cli/skill_watcher.py | 🟡 |
| 에이전트 관리 | cli/main.py | 🟡 |
| 컨텍스트 카테고리 | scripts/context_loader.py | 🟡 |
| 토큰 추정기 | scripts/token_estimator.py | 🟡 |

---

## 6. 테스트 계획

### 6.1 프론트매터 파싱 테스트

```python
# tests/unit/test_frontmatter.py
import pytest
from superclaude.hooks.inline_hooks import parse_inline_hooks

def test_parse_context_fork():
    fm = {'context': 'fork'}
    assert fm['context'] == 'fork'

def test_parse_agent_field():
    fm = {'agent': 'backend-architect'}
    assert fm['agent'] in VALID_AGENTS

def test_parse_inline_hooks():
    fm = {
        'hooks': {
            'PreToolUse': [{'type': 'command', 'command': 'echo test'}]
        }
    }
    hooks = parse_inline_hooks(fm)
    assert 'PreToolUse' in hooks
    assert len(hooks['PreToolUse']) == 1
```

### 6.2 통합 테스트

```python
# tests/integration/test_skill_execution.py
def test_forked_skill_execution():
    """context: fork 스킬 실행 테스트"""
    pass

def test_agent_routing():
    """agent 필드 기반 라우팅 테스트"""
    pass
```

---

## 7. 참조

### 7.1 관련 파일

| 파일 | 역할 |
|------|------|
| `src/superclaude/skills/confidence-check/SKILL.md` | 스킬 프론트매터 예시 |
| `src/superclaude/agents/pm-agent.md` | 에이전트 정의 예시 |
| `src/superclaude/hooks/hooks.json` | 훅 설정 |
| `src/superclaude/scripts/skill_activator.py` | 스킬 활성화 로직 |
| `src/superclaude/cli/install_skill.py` | 스킬 설치 CLI |

### 7.2 Claude Code 문서

- [Claude Code v2.1.0 Release Notes](https://docs.anthropic.com/claude-code/releases)
- [Skill Frontmatter Specification](https://docs.anthropic.com/claude-code/skills)
- [Hook System Reference](https://docs.anthropic.com/claude-code/hooks)

---

## 8. 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| 1.0.0 | 2026-01-08 | 초기 문서 작성 |
