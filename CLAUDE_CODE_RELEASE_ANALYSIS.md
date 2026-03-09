# Claude Code 최근 릴리즈 분석 (v2.1.47 ~ v2.1.71)

> 분석일: 2026-03-08 | 분석 범위: 최근 약 1개월간 업데이트

---

## 요약

최근 한 달간 Claude Code는 **모델 업그레이드**(Opus 4.6, Sonnet 4.6), **멀티에이전트 협업**, **자동 메모리**, **워크트리 격리** 등 대규모 기능 추가와 함께, Windows 안정성 및 메모리 최적화에 집중한 업데이트를 진행했습니다.

---

## Tier 1 — 핵심 신규 기능

### 1. Opus 4.6 + Effort Control

**버전**: v2.1.32 (모델), v2.1.36 (fast mode), v2.1.68 (effort 기본값)

Claude Opus 4.6이 새로운 기본 모델로 도입되었으며, 작업 복잡도에 따라 사고 강도를 조절할 수 있습니다.

#### Effort 레벨

| 레벨 | 트리거 | 적합한 작업 |
|------|--------|------------|
| Medium (기본) | 자동 적용 | 일반 코딩, 리뷰, 편집 |
| High | 프롬프트에 `ultrathink` 입력 | 복잡한 아키텍처 설계, 디버깅, 보안 분석 |
| Fast | `/fast` 토글 | 타입 추가, 이름 변경, 간단한 수정 |

#### 사용 예시

```
# 복잡한 문제 — high effort
ultrathink 이 distributed lock의 race condition을 분석하고 해결책을 제시해

# 간단한 작업 — fast mode 토글
/fast
이 파일의 import 정리해

# effort 설정 확인/변경
/model
```

#### 권장 워크플로우

1. 기본(medium)으로 시작
2. 복잡한 문제에만 `ultrathink` 사용
3. 반복적/기계적 작업은 `/fast` 활용
4. `/model`에서 기본 effort 변경 가능

---

### 2. Agent Teams (다중 에이전트 협업)

**버전**: v2.1.32 | **상태**: 실험적 (research preview)

여러 에이전트가 동시에 병렬로 작업할 수 있는 기능입니다.

#### 설정

```bash
# 환경 변수 설정
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
claude
```

#### 사용 예시

```
# 프론트엔드/백엔드 동시 리팩토링
"auth 모듈의 프론트엔드 컴포넌트와 백엔드 API를 동시에 리팩토링해"

# 테스트 + 구현 병렬
"새 payment API를 구현하면서 동시에 테스트도 작성해"
```

#### 키보드 조작

| 단축키 | 동작 |
|--------|------|
| Shift+Down | teammate 간 이동 (순환) |
| Ctrl+F | 백그라운드 에이전트 전체 종료 (2회 확인) |
| Ctrl+B | 현재 작업 백그라운드로 전환 |

#### Agent 정의에서 모델 지정

```markdown
<!-- .claude/agents/frontend-worker.md -->
---
model: claude-sonnet-4-6
---
프론트엔드 전문 에이전트입니다...
```

---

### 3. Auto Memory (자동 메모리)

**버전**: v2.1.32 (도입), v2.1.59 (안정화)

Claude가 작업하면서 유용한 패턴, 결정, 선호도를 **자동으로 저장**합니다.

#### 동작 방식

- 별도 설정 불필요 — 자동 작동
- 세션 간 자동 유지
- 프로젝트별 컨텍스트 분리

#### 관리

```
/memory              # 저장된 메모리 확인/편집
/memory edit         # 직접 편집 모드
```

#### 저장되는 정보 예시

- 프로젝트 코딩 컨벤션 (들여쓰기, 네이밍 등)
- 자주 사용하는 명령어 패턴
- 아키텍처 결정 사항
- 디버깅 과정에서 발견한 인사이트

---

### 4. Worktree Isolation (워크트리 격리)

**버전**: v2.1.49

Git worktree를 활용해 메인 브랜치에 영향 없이 안전하게 실험할 수 있습니다.

#### CLI에서 사용

```bash
# 격리 모드로 Claude 시작
claude --worktree
claude -w
```

#### Agent 정의에서 사용

```markdown
<!-- .claude/agents/risky-refactor.md -->
---
isolation: worktree
---
대규모 리팩토링을 격리된 환경에서 수행하는 에이전트입니다.
변경이 완료되면 워크트리 경로와 브랜치 정보를 반환합니다.
```

#### 서브에이전트 격리

```
# Agent tool 호출 시 isolation 파라미터 사용
# 임시 worktree에서 독립 작업 후 결과만 반환
```

#### 권장 시나리오

- 대규모 리팩토링
- 실험적 기능 구현
- 여러 접근법 비교 테스트
- 위험도 높은 마이그레이션

---

## Tier 2 — 생산성 향상 기능

### 5. /loop 명령 (반복 실행)

**버전**: v2.1.71

프롬프트나 슬래시 명령을 주기적으로 반복 실행합니다.

```
/loop 5m 배포 상태 확인해          # 5분마다 배포 체크
/loop 10m uv run pytest -v        # 10분마다 테스트 실행
/loop 3m git log --oneline -3     # 3분마다 최근 커밋 확인
/loop 5m /sc:test                 # 5분마다 테스트 스킬 실행
```

- 기본 간격: 10분 (미지정 시)
- 세션 내 cron 스케줄링도 가능

---

### 6. Skills Hot-Reload (스킬 즉시 반영)

**버전**: v2.1.0

```bash
# 스킬 생성/수정 → 즉시 사용 가능 (재시작 불필요)
~/.claude/skills/my-skill/SKILL.md

# fork 컨텍스트로 격리 실행
---
context: fork
agent: backend-architect
user-invocable: true
---

# 스킬 디렉토리 자기참조
${CLAUDE_SKILL_DIR}/templates/...
```

---

### 7. PR Status Indicator

**버전**: v2.1.20

프롬프트 하단에 현재 브랜치의 PR 상태가 자동 표시됩니다.

| 색상 | 상태 |
|------|------|
| 🟢 녹색 | Approved |
| 🟡 노란색 | Pending Review |
| 🔴 빨간색 | Changes Requested |
| ⚪ 회색 | Draft |
| 🟣 보라색 | Merged |

- 클릭 가능한 링크 포함
- 설정 불필요 — `gh` CLI가 있으면 자동 작동

---

### 8. Named Sessions (세션 이름 지정)

**버전**: v2.0.64

```bash
# 현재 세션에 이름 부여
/rename auth-refactor-v2

# 나중에 이름으로 재개
claude --resume auth-refactor-v2
/resume auth-refactor-v2

# 인수 없이 호출하면 대화 컨텍스트 기반 자동 이름 생성
/rename
```

---

### 9. /copy Interactive Picker

**버전**: v2.0.64, v2.1.64 (개선)

```
/copy
# → 응답 내 코드 블록 목록 표시
# → 개별 블록 선택 또는 전체 응답 복사
# → "Always copy full response" 옵션으로 기본값 설정
```

---

## Tier 3 — 개발자 경험(DX) 개선

### 주요 명령어 요약

| 명령 | 버전 | 설명 | 예시 |
|------|------|------|------|
| `/debug` | v2.1.30 | 세션 문제 자체 진단 | `/debug` |
| `/keybindings` | v2.1.18 | 키보드 단축키 커스터마이징 | `/keybindings` |
| `/stats` | v2.1.6 | 사용 통계 (`r`로 기간 전환) | `/stats` |
| `/simplify` | v2.1.63 | 코드 간소화 분석 | `/simplify` |
| `/batch` | v2.1.63 | 일괄 작업 처리 | `/batch` |
| `/context` | v2.0.86 | 토큰 예산 시각화 | `/context` |
| `/rewind` | v2.0.0 | 코드 변경 되돌리기 | `/rewind` |
| `/plan` | v2.1.0 | 플랜 모드 진입 | `/plan` |

### 주요 단축키

| 단축키 | 동작 |
|--------|------|
| Ctrl+R | 히스토리 검색 |
| Ctrl+B | bash/에이전트 백그라운드 실행 |
| Ctrl+G | 외부 에디터로 프롬프트 편집 |
| Ctrl+O | 트랜스크립트 모드 토글 |
| Ctrl+F | 백그라운드 에이전트 종료 |
| Alt+T | 사고(thinking) 모드 토글 |
| Alt+P | 프롬프트 작성 중 모델 전환 |
| Shift+Tab | 퍼미션 모드 전환 (Windows) |

---

## Windows 관련 주요 수정사항

이 환경(Windows 11)에 직접 관련된 개선:

| 버전 | 수정 내용 |
|------|----------|
| v2.1.47 | Hooks가 Git Bash를 사용하여 정상 작동 |
| v2.1.47 | `\r\n` 줄바꿈으로 인한 렌더링 문제 해결 |
| v2.1.47 | WSL2 BMP 이미지 붙여넣기 수정 |
| v2.1.47 | Bash 출력이 MSYS2/Cygwin에서 정상 표시 |
| v2.1.41 | Windows ARM64 네이티브 바이너리 지원 |
| v2.1.27 | 콘솔 윈도우 깜빡임 해결 |
| v2.1.47 | 드라이브 문자 대소문자 비교 수정 |
| v2.1.51 | BashTool 로그인 셸 스킵으로 성능 향상 |
| v2.1.69 | 클립보드 비ASCII 문자(CJK, 이모지) 손상 수정 |

---

## 보안 관련 수정

| 버전 | 내용 | 심각도 |
|------|------|--------|
| v2.1.47 | Bash 권한 체크 우회 수정 | 🔴 |
| v2.1.38 | Heredoc 구분자 파싱 명령 주입 방지 | 🔴 |
| v2.1.7 | 와일드카드 권한 매칭 복합 명령 수정 | 🔴 |
| v2.1.69 | acceptEdits 모드 심링크 우회 수정 | 🔴 |
| v2.1.51 | statusLine/fileSuggestion 훅 신뢰 검사 | 🟡 |

---

## 성능 개선

| 영역 | 개선 내용 |
|------|----------|
| 메모리 | 3배 메모리 사용량 개선 (v2.1.70) |
| WASM | tree-sitter 파서 주기적 리셋으로 메모리 누수 해결 |
| 렌더링 | React Compiler 적용으로 UI 성능 향상 |
| 시작 | 여러 버전에 걸쳐 시작 시간 단축 |
| 컴팩션 | 자동 컴팩션 즉시 실행 (v2.0.64) |

---

## 즉시 적용 권장 체크리스트

- [ ] `/fast` 토글 — 간단한 작업에서 속도 향상 체감
- [ ] `ultrathink` — 다음 복잡한 디버깅 세션에서 시도
- [ ] `/memory` — auto memory가 무엇을 저장했는지 확인
- [ ] `claude -w` — 다음 리팩토링에 worktree 격리 사용
- [ ] `/loop` — CI/CD 모니터링에 활용
- [ ] `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` — 대규모 작업에 멀티에이전트 시도
- [ ] `/keybindings` — 자주 쓰는 단축키 커스터마이징
- [ ] `/rename` — 중요한 세션에 이름 부여하여 나중에 쉽게 재개
