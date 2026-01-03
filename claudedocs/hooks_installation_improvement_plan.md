# Hooks Installation Improvement Plan

> **Date**: 2026-01-03
> **Status**: Planning
> **Related**: `claude_code_hooks_guide.md`

## 1. Problem Statement

### Discovery
Claude Code에서 hooks 처리 방식에 차이가 있음:

| 설치 방식 | hooks.json 처리 | settings.json 병합 |
|-----------|-----------------|-------------------|
| Plugin (`/plugin install`) | 자동 로드 | **자동 병합** |
| Normal (`superclaude install`) | `.claude/hooks/hooks.json` 복사 | **병합 없음** |

### Current Behavior
```
superclaude install --scope [user|project]
    │
    ├─► src/superclaude/scripts/ → .claude/superclaude/scripts/  ✓
    ├─► src/superclaude/hooks/hooks.json → .claude/hooks/hooks.json  ✓
    │   ({{SCRIPTS_PATH}} 치환 완료)
    │
    └─► .claude/settings.json  ✗ 병합 없음!
```

### Impact
- Claude Code가 `.claude/hooks/hooks.json`을 자동 로드하지 않을 경우, hooks 미작동
- 사용자가 수동으로 settings.json에 hooks 추가 필요
- Plugin 설치 방식과 일반 설치 방식 간 동작 불일치

---

## 2. Research Findings

### 2.1 Claude Code Hooks Configuration

**공식 설정 위치** (우선순위 높은 순):
1. `.claude/settings.local.json` - 프로젝트별 로컬 (gitignore)
2. `.claude/settings.json` - 프로젝트별 공유
3. `~/.claude/settings.json` - 사용자 전역

**Hooks 구조**:
```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          { "type": "command", "command": "...", "timeout": 10 }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          { "type": "command", "command": "...", "timeout": 30 }
        ]
      }
    ]
  }
}
```

### 2.2 Current Implementation Analysis

**File**: `src/superclaude/cli/install_commands.py`

**Function**: `install_hooks_and_scripts()` (lines 210-305)

```python
# 현재 동작 (lines 247-250):
if scope == "project":
    scripts_path_for_hooks = ".claude/superclaude/scripts"
else:
    scripts_path_for_hooks = str(scripts_target.resolve())

# hooks.json 복사만 수행 (lines 275-301)
# settings.json 병합 로직 없음!
```

### 2.3 Sources
- [Claude Code Tips - Hooks](https://dev.to/damogallagher/the-ultimate-claude-code-tips-collection-advent-of-claude-2025-5b73)
- [Claude Code Configuration Guide](https://www.claudelog.com/configuration/)
- [Claude Code VS Code Docs](https://code.claude.com/docs/en/vs-code)

---

## 3. Scope-Based Rules

### 3.1 Scope Summary

| Scope | Base Path | settings.json | Scripts Path Format |
|-------|-----------|---------------|---------------------|
| `user` | `~/.claude/` | `~/.claude/settings.json` | Absolute |
| `project` | `./.claude/` | `./.claude/settings.json` | Relative |
| `target` | `{path}/.claude/` | `{path}/.claude/settings.json` | Absolute |

### 3.2 Path Format Rules

```
┌────────────────────────────────────────────────────────────────────┐
│ RULE 1: user scope                                                 │
│ command: "python ~/.claude/superclaude/scripts/session_init.py"    │
│          ↑ Absolute path (works from any directory)                │
├────────────────────────────────────────────────────────────────────┤
│ RULE 2: project scope                                              │
│ command: "python .claude/superclaude/scripts/session_init.py"      │
│          ↑ Relative path (works only from project root)            │
├────────────────────────────────────────────────────────────────────┤
│ RULE 3: target scope                                               │
│ command: "python /path/to/proj/.claude/superclaude/scripts/..."    │
│          ↑ Absolute path (based on target path)                    │
└────────────────────────────────────────────────────────────────────┘
```

### 3.3 Merge Strategy

**Preservation Rule**: 기존 사용자 hooks 보존

```
Before (user settings):
{
  "hooks": {
    "PostToolUse": [
      { "hooks": [{ "command": "npm run lint" }] }  ← User hook
    ]
  }
}

After (merged):
{
  "hooks": {
    "PostToolUse": [
      { "hooks": [{ "command": "npm run lint" }] },    ← Preserved
      { "matcher": "Edit|Write",                       ← SuperClaude added
        "hooks": [{ "command": "python ..." }] }
    ],
    "SessionStart": [...],      ← SuperClaude new
    "UserPromptSubmit": [...]   ← SuperClaude new
  }
}
```

### 3.4 Idempotency Rules

| Condition | `--force=False` | `--force=True` |
|-----------|-----------------|----------------|
| No SuperClaude hooks | Add | Add |
| SuperClaude hooks exist | **Skip** | Replace |
| User hooks | Preserve | Preserve |

### 3.5 SuperClaude Hook Identification

```python
SUPERCLAUDE_MARKERS = [
    "superclaude",
    "session_init",
    "skill_activator",
    "prettier_hook"
]

def _is_superclaude_hook(hook_entry: dict) -> bool:
    for hook in hook_entry.get("hooks", []):
        cmd = hook.get("command", "")
        if any(marker in cmd for marker in SUPERCLAUDE_MARKERS):
            return True
    return False
```

---

## 4. Implementation Plan

### 4.1 New Functions to Add

#### `merge_hooks_to_settings()`
```python
def merge_hooks_to_settings(
    base_path: Path,
    hooks_config: dict,
    scope: str,           # "user" | "project" | "target"
    force: bool = False
) -> Tuple[bool, str]:
    """
    Merge hooks.json content into settings.json

    Args:
        base_path: Installation base path (.claude directory)
        hooks_config: Transformed hooks config (paths already applied)
        scope: Installation scope
        force: Replace existing SuperClaude hooks if True

    Returns:
        Tuple of (success, message)

    Flow:
        1. Load existing settings.json (or {} if not exists)
        2. Identify SuperClaude hooks in existing config
        3. Merge new hooks with existing (preserve user hooks)
        4. Save updated settings.json
    """
```

#### `_is_superclaude_hook()`
```python
def _is_superclaude_hook(hook_entry: dict) -> bool:
    """Identify if a hook entry belongs to SuperClaude"""
```

#### `_merge_hook_arrays()`
```python
def _merge_hook_arrays(
    existing: List[dict],
    new: List[dict],
    force: bool
) -> List[dict]:
    """Merge two hook arrays, preserving user hooks"""
```

### 4.2 Modified Functions

#### `install_hooks_and_scripts()`

```diff
  # After hooks.json copy (line ~300):

+ # Merge hooks to settings.json
+ hooks_data = json.loads(content)
+ merge_success, merge_msg = merge_hooks_to_settings(
+     base_path=base_path,
+     hooks_config=hooks_data,
+     scope=scope,
+     force=force
+ )
+ if merge_success:
+     installed += 1
+     messages.append(merge_msg)
+ else:
+     failed += 1
+     messages.append(f"Failed to merge hooks: {merge_msg}")
```

### 4.3 Call Flow

```
install_hooks_and_scripts(base_path, force, scope)
    │
    ├─► Copy scripts to .claude/superclaude/scripts/
    │
    ├─► Transform hooks.json ({{SCRIPTS_PATH}} → actual path)
    │
    ├─► Copy hooks.json to .claude/hooks/hooks.json (existing)
    │
    └─► merge_hooks_to_settings(base_path, hooks_config, scope, force)  ← NEW
            │
            ├─► Load settings.json
            ├─► Identify existing SuperClaude hooks
            ├─► Merge (preserve user hooks)
            └─► Save settings.json
```

---

## 5. Test Cases

### 5.1 Scope Tests

| Test | Scope | Condition | Expected |
|------|-------|-----------|----------|
| T1 | user | No settings.json | Create with hooks |
| T2 | user | Empty settings.json | Add hooks section |
| T3 | user | Existing user hooks | Preserve + add SuperClaude |
| T4 | project | Relative paths | `.claude/superclaude/scripts/...` |
| T5 | target | Absolute paths | `/path/to/.claude/superclaude/scripts/...` |

### 5.2 Merge Tests

| Test | Condition | Expected |
|------|-----------|----------|
| M1 | First install | All hooks added |
| M2 | Reinstall (no force) | Skip existing SuperClaude |
| M3 | Reinstall (force) | Replace SuperClaude hooks |
| M4 | User hooks exist | Preserve user, add SuperClaude |

### 5.3 Edge Cases

| Test | Condition | Expected |
|------|-----------|----------|
| E1 | Malformed settings.json | Error message, no crash |
| E2 | Read-only settings.json | Error message |
| E3 | Windows paths | Proper backslash handling |

---

## 6. Files to Modify

| File | Changes | Complexity |
|------|---------|------------|
| `src/superclaude/cli/install_commands.py` | Add merge functions, modify install_hooks_and_scripts | Medium |
| `tests/cli/test_install_commands.py` | Add test cases | Medium |
| `install.sh` | Update comments | Low |

---

## 7. Risk Analysis

| Risk | Level | Mitigation |
|------|-------|------------|
| Corrupt existing settings.json | LOW | Backup before merge |
| Lose user hooks | LOW | Merge-only, no delete |
| Windows path issues | LOW | Use pathlib |
| JSON parse errors | LOW | Try/except with clear error |

---

## 8. Implementation Checklist

- [ ] Add `SUPERCLAUDE_MARKERS` constant
- [ ] Add `_is_superclaude_hook()` helper
- [ ] Add `_merge_hook_arrays()` helper
- [ ] Add `merge_hooks_to_settings()` main function
- [ ] Modify `install_hooks_and_scripts()` to call merge
- [ ] Add unit tests for new functions
- [ ] Add integration tests for each scope
- [ ] Update install.sh comments
- [ ] Test on Windows
- [ ] Test on Unix/Mac

---

## 9. Appendix

### A. Current hooks.json Template

```json
{
  "description": "SuperClaude hooks for session management and code formatting",
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python {{SCRIPTS_PATH}}/session_init.py",
            "timeout": 10
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python {{SCRIPTS_PATH}}/skill_activator.py",
            "timeout": 5
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "python {{SCRIPTS_PATH}}/prettier_hook.py",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

### B. Expected settings.json After Merge (user scope)

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python /home/user/.claude/superclaude/scripts/session_init.py",
            "timeout": 10
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python /home/user/.claude/superclaude/scripts/skill_activator.py",
            "timeout": 5
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "python /home/user/.claude/superclaude/scripts/prettier_hook.py",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```
