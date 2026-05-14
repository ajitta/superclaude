---
status: implemented
revised: 2026-04-08
---

# Living Gotchas Architecture — Discovery Spec

## Problem Statement

SuperClaude의 gotchas(Claude가 반복하는 실패 패턴)는 현재 프레임워크 파일에 하드코딩되어 있다. 모든 프로젝트에 동일한 gotchas가 적용되며, 프로젝트별 실패 패턴을 담을 구조가 없다.

하네스 엔지니어링의 핵심 원칙 — "에이전트가 실수를 할 때마다 그 실수가 다시는 반복되지 않도록 하는 것" — 을 실현하려면, gotchas가 **관찰된 실패로부터 성장하는 살아있는 시스템**이어야 한다.

## Source Documents

- 하네스 공식문서 100번 읽은 것처럼 만들어드림 (캐슬AI, 2026-04-03)
- Claude AI 협업형 프롬프트 사용법 (헤이제임스, 2026-04-07)
- Claude Code 스킬, 만든 사람들은 이렇게 쓰고 있었다 (AgentOS, 2026-03-21)

## Research Findings

| 발견 | 소스 | 신뢰도 |
|------|------|--------|
| `paths:` frontmatter → 조건부 로딩 | Anthropic 공식 docs + 4 독립 소스 | High (실사용 확인) |
| `.claude/rules/` 서브디렉토리 재귀 스캔 | 공식 docs에 `frontend/`, `backend/` 예시 | High |
| 모듈 파일(50줄) 96% 준수율 vs 단일 파일 92% | SFEIR Institute 실증 데이터 | Medium-High |
| ~150 total instructions → 준수율 저하 | 다수 practitioner 보고 | Medium |
| rules 파일당 ~1K tokens 권장 | Anthropic 엔지니어 HN 코멘트 | Medium-High |
| Gotchas = 스킬에서 가장 가치 있는 콘텐츠 | Anthropic 공식 스킬 가이드 | High |

## Design: 3-Layer Gotcha Architecture

### Layer Overview

```
Layer 3: Personal ──→ auto memory (feedback type)
  "응답 짧게", "snake_case 선호"
  개인만, 현재 R14 유지

Layer 2: Project ──→ .claude/rules/gotchas/*.md + paths: 스코핑  ★ NEW
  "pytest-django 필수", "SQLAlchemy 2.0만"
  팀 공유 (git), CC 네이티브 조건부 로딩

Layer 1: Framework ─→ command/agent .md <gotchas>
  "evidence-fabrication", "seq-loop"
  SC 배포, 모든 사용자 동일
```

### Layer 1: Framework Gotchas (기존, 변경 없음)

- **위치**: `src/superclaude/commands/*.md`, `agents/*.md`, `skills/*/SKILL.md`의 `<gotchas>` 섹션
- **범위**: Claude의 범용 행동 실패 패턴
- **예시**: evidence-fabrication, seq-loop, scope-creep, pre-assign
- **수명주기**: SC 관리자가 작성, `make deploy`로 배포
- **공유**: 모든 SuperClaude 사용자 동일

### Layer 2: Project Gotchas (신규)

- **위치**: `.claude/rules/gotchas/*.md`
- **범위**: 특정 프로젝트의 트랩과 컨벤션
- **로딩**: CC 네이티브 — `paths:` frontmatter로 조건부 로딩
- **공유**: git commit → 팀 전체
- **한도**: 전체 합산 100줄 이하 권장 (파일당 50줄 이하)

#### 디렉토리 구조

```
.claude/rules/
├── agent-authoring.md        ← 기존 SC authoring rules
├── command-authoring.md
├── mode-authoring.md
├── skill-authoring.md
└── gotchas/                  ← NEW
    └── general.md            ← /sc:init이 생성하는 유일한 파일
```

도메인별 파일(database.md, frontend.md 등)은 R14가 처음 제안할 때 자동 생성된다. 미리 만들지 않음.

#### 파일 형식

```yaml
---
paths:
  - "**/models/**"
  - "**/migration*"
---
# Database Gotchas
# Last reviewed: 2026-04-08

- orm-style: SQLAlchemy 2.0 스타일만 사용 (select(Model).where()), legacy Query API 금지
- migration-order: 모델 변경 전 항상 makemigrations 먼저 실행
```

#### general.md (frontmatter 없음 → 항상 로딩)

```markdown
# Project Gotchas — General
# Claude가 실수할 때마다 여기에 한 줄씩 추가됩니다.
# 기존에 알려진 프로젝트 트랩이 있으면 직접 추가 가능 (R14 자동 캡처와 병행).
```

frontmatter가 없는 rules 파일은 CC가 무조건 로딩한다. 빈 frontmatter(`---\n---`)는 파싱 예측 불가하므로 생략.

### Layer 3: Personal Gotchas (기존, 변경 없음)

- **위치**: `~/.claude/projects/*/memory/` (auto memory, feedback type)
- **범위**: 사용자 개인의 작업 스타일과 선호
- **예시**: "terse 응답 선호", "snake_case 선호"
- **수명주기**: R14 자동 저장 (현재 동작 유지)

## Capture Mechanism: Enhanced R14

### 현재 R14

```
user corrects Claude → save feedback memory (personal) → 끝
```

### 제안 R14

```
user corrects Claude
  → 프로젝트 특정 패턴인가? (파일/패키지/패턴 언급)
  │
  ├─ YES → Claude가 적절한 gotchas 파일 제안
  │   "이걸 .claude/rules/gotchas/database.md에 추가할까요?
  │    `orm-style: SQLAlchemy 2.0 스타일만 사용`"
  │   → 해당 파일이 없으면 paths: 포함한 새 파일 생성 제안
  │   → 사용자 승인 → append
  │
  ├─ AMBIGUOUS → Layer 2 (project) 우선 제안
  │   이유: 팀에 유용할 가능성 높고, 불필요시 삭제 가능
  │
  └─ NO (스타일/선호) → auto memory 저장 (현재 동작)
```

### 분류 시그널

| 시그널 | → Project (Layer 2) | → Personal (Layer 3) |
|--------|:---:|:---:|
| 특정 파일, 패키지, 패턴 언급 | ✅ | |
| "이 프로젝트에선", "우리 팀은" | ✅ | |
| 코드 패턴/아키텍처 교정 | ✅ | |
| 커뮤니케이션 스타일 | | ✅ |
| "나는", "내가 선호하는" | | ✅ |
| 프로젝트 참조 없는 선호 | | ✅ |
| **모호한 경우** | **✅ 우선** | |

### 핵심 원칙

- **파일 제안 = 분류**: 별도 분류 로직 불필요. Claude가 적절한 gotchas 파일을 제안하는 행위 자체가 분류
- **사용자 승인 필수**: 자동으로 파일 수정하지 않음. 항상 제안 후 승인
- **파일 자동 생성**: 해당 도메인 gotchas 파일이 없으면 `paths:` 포함하여 새로 생성 제안

## Gardening Convention (노후화 방지)

- 각 파일 상단에 `# Last reviewed: YYYY-MM-DD` 주석
- `/sc:reflect`에서 3개월+ 미검토 gotchas 파일 경고
- 코드에 없는 파일/함수 참조 gotcha → audit 시 감지
- `paths:` 패턴 노후화 감지: 프로젝트 구조 변경(디렉토리 리네임) 시 gotchas 파일의 `paths:` 글로브 패턴도 함께 업데이트. `/sc:reflect`에서 gotchas 파일의 `paths:` 패턴이 현재 프로젝트에 매칭되는 파일이 있는지 확인
- 분기별 정리 권장: "이 gotcha가 여전히 필요한가?"

## Implementation Touch-points

| # | 항목 | 변경 내용 | 파일 |
|---|------|----------|------|
| 1 | /sc:init 메뉴 확장 | task `[h] Project gotchas initialization` 추가 — gotchas/general.md 생성 | `src/superclaude/commands/init.md` (markdown만 수정) |
| 2 | R19 신규 규칙 | Project Gotcha Capture — R14(personal memory)와 분리된 독립 규칙 | `src/superclaude/core/RULES.md` |
| 3 | 컨벤션 문서화 | 3-layer gotcha 구조 + gotchas/ 디렉토리 설명 | `CLAUDE.md` 또는 새 authoring rule |
| 4 | /sc:reflect 가드닝 | 3개월+ 미검토 gotchas 파일 경고 + paths: 패턴 매칭 확인 | `src/superclaude/commands/reflect.md` |

- 새 커맨드: 불필요
- 새 스킬: 불필요
- context_loader 변경: 불필요
- 새 hook 스크립트: 불필요
- Python 코드 변경: 불필요 (모든 touch-point가 markdown 수정)

## Design Decisions

| 결정 | 선택 | 대안 | 이유 |
|------|------|------|------|
| Layer 2 위치 | `.claude/rules/gotchas/` | CLAUDE.md 섹션 | SC install 파이프라인과 독립, 덮어씌기 방지 |
| 섹션 구분 | 도메인별 별도 파일 | 커맨드별 섹션 | `paths:` 조건부 로딩 활용, 중복 방지 |
| 캡처 방식 | 파일 제안 + 사용자 승인 | 자동 분류 + 사후 알림 | 교정 순간 friction 최소화, 오분류 방지 |
| 모호한 경우 | Layer 2 우선 | 물어보기 | 팀 공유 가치 > 개인 저장, 삭제 가능 |
| 초기 템플릿 | general.md만 | 모든 도메인 미리 생성 | 빈 파일 방치 방지, 필요 시 R14가 생성 |
| 노후화 관리 | reviewed 주석 + reflect 경고 | 자동 삭제 | 안전한 수동 판단, 자동 삭제는 위험 |
| Layer 충돌 | Layer 2 (project) > Layer 3 (personal) | 동일 우선순위 | 팀 규칙이 개인 선호보다 우선 |
| Layer 중복 | 경고만, 차단 안함 | 자동 제거 | R14가 중복 감지 시 "이미 framework gotcha에 있습니다" 알림 |
| Gotcha 형식 | `name: description` (framework gotchas와 동일) | 자유 형식 | 일관성 + grep 가능성 확보 |

## Validation Criteria

- [ ] `paths:` 조건부 로딩이 프로젝트 레벨 `.claude/rules/`에서 동작 확인
- [ ] gotchas/ 서브디렉토리의 .md 파일이 CC에 의해 로딩됨 확인
- [ ] R19 신규 규칙 후 교정 시 gotchas 파일 추가 제안이 자연스럽게 동작
- [ ] 기존 테스트 스위트 영향 없음 (마크다운 변경만)
- [ ] /sc:init이 gotchas/general.md를 정상 생성
- [ ] 특정 gotcha 추가 후 Claude가 해당 패턴을 회피하는지 수동 검증 (1-2 케이스)

## Scope Boundaries

**In scope**: Layer 2 구조 정의, R19 신규 규칙 (R14 유지, 별도 추가), init 템플릿, gardening 컨벤션
**Out of scope**: Layer 1 변경, auto memory 구조 변경, 자동 gotcha 감지/ML, enforcement hooks (Tier 1 of previous brainstorm — separate spec)

## Handoff

이 spec 승인 후: `/sc:plan` → 구현 계획 수립
관련 후속 작업: On-Demand Enforcement Skills (별도 spec), Harness Self-Audit (별도 spec)
