# 하네스 엔지니어링 프레임워크 가이드

> **목적**: AI 코딩 에이전트(Claude Code 등)와 협업하는 개발자를 위한 실무 프레임워크
> **핵심 원칙**: 에이전트가 실수하면, 같은 실수를 다시 못하게 환경을 엔지니어링한다
> **최종 수정**: 2026-03

---

## 1. 개요

### 1.1 하네스 엔지니어링이란

하네스 엔지니어링은 AI 코딩 에이전트가 안정적으로 작업할 수 있도록 **환경 전체를 설계하는 엔지니어링 분야**다. 프롬프트 하나를 잘 쓰는 것이 아니라, 에이전트를 둘러싼 제약·도구·문서·피드백 루프의 총합을 체계적으로 구축한다.

하네스(harness)라는 용어는 2026년 2월 Mitchell Hashimoto(HashiCorp 창업자)가 블로그에서 명명했고, 같은 주에 OpenAI가 "Harness engineering: leveraging Codex in an agent-first world"라는 제목으로 상세 사례를 공개하면서 업계에 급속히 확산되었다.

### 1.2 왜 필요한가

같은 모델이라도 프로젝트 A에서는 잘 동작하고 프로젝트 B에서는 이상한 결과를 낸다. 프롬프트 튜닝으로 그 격차를 좁히지 못할 때, 원인은 대개 에이전트를 둘러싼 **환경의 차이**에 있다. 하네스 엔지니어링은 이 환경을 의도적으로 설계하는 것이다.

### 1.3 진화 경로

| 단계 | 시기 | 설계 대상 | 핵심 활동 |
|------|------|-----------|-----------|
| 프롬프트 엔지니어링 | 2023~2024 | 입력 텍스트 | 질문 하나, 응답 하나의 최적화 |
| 컨텍스트 엔지니어링 | 2025 중반 | 시스템 전체 맥락 | RAG, MCP, 메모리를 통한 맥락 설계 |
| 하네스 엔지니어링 | 2026.02~ | 에이전트 실행 환경 전체 | 제약, 도구, 문서, 피드백 루프 통합 설계 |

### 1.4 핵심 역설

> 에이전트에게 더 많은 제약을 부여할수록, 출력은 더 신뢰할 수 있게 된다.

자유도를 줄이는 것이 곧 품질을 높이는 것이다. 이것이 하네스 엔지니어링의 가장 반직관적이면서도 가장 중요한 통찰이다.

---

## 2. 하네스의 4대 구성요소

```
┌─────────────────────────────────────────────────────┐
│                    하네스 (Harness)                    │
│                                                       │
│  ┌──────────────┐  ┌──────────────┐                  │
│  │  1. 지침 파일  │  │ 2. 결정론적   │                  │
│  │  (CLAUDE.md)  │  │    도구/검증   │                  │
│  └──────────────┘  └──────────────┘                  │
│                                                       │
│  ┌──────────────┐  ┌──────────────┐                  │
│  │ 3. 아키텍처   │  │ 4. 피드백 루프 │                  │
│  │    제약       │  │   및 관찰     │                  │
│  └──────────────┘  └──────────────┘                  │
│                                                       │
│           [ AI 코딩 에이전트 (Claude) ]                 │
└─────────────────────────────────────────────────────┘
```

---

## 3. 구성요소 1: 지침 파일 (CLAUDE.md)

### 3.1 역할

CLAUDE.md는 에이전트가 매 세션 시작 시 자동으로 읽는 **프로젝트 컨텍스트 파일**이다. 백과사전이 아니라 **목차(table of contents)** 역할을 해야 한다. 상세 내용은 별도 문서를 참조하도록 포인터를 제공한다.

### 3.2 설계 원칙

- **100줄 이내로 유지**: 컨텍스트는 희소 자원이다. 거대한 지침 파일은 실제 작업 코드와 태스크 설명을 밀어낸다.
- **실패 기반 누적 업데이트**: 에이전트가 실수할 때마다 해당 실수를 방지하는 규칙을 즉시 추가한다.
- **포인터 구조**: 설계 문서, 아키텍처 맵, 품질 기준 등 상세 정보는 `docs/` 디렉토리에 두고 CLAUDE.md에서 참조만 한다.

### 3.3 템플릿

```markdown
# CLAUDE.md

## 프로젝트 개요
- 프로젝트명: [프로젝트명]
- 기술 스택: [예: TypeScript, Next.js 15, PostgreSQL]
- 아키텍처 유형: [예: 모놀리식 / 마이크로서비스 / 모듈러 모놀리스]

## 빌드 및 실행
- 전체 빌드: `pnpm build`
- 개발 서버: `pnpm dev`
- 테스트 실행: `pnpm test`
- 린트: `pnpm lint`

## 코딩 규칙
- 패키지 의존 방향: domain → application → infrastructure
- infrastructure는 domain을 직접 참조하지 않는다
- 컴포넌트는 함수형으로 작성하며, 클래스 컴포넌트는 사용하지 않는다
- API 응답은 반드시 타입 정의 후 사용한다
- [여기에 에이전트 실패 시마다 규칙 추가]

## 금지 패턴
- `any` 타입 사용 금지
- `console.log`를 프로덕션 코드에 남기지 않는다
- 직접 DOM 조작 금지 (React 환경)
- [여기에 에이전트가 반복한 실수 패턴 추가]

## 커밋 규칙
- 커밋 메시지는 한국어로 작성, 마침표 생략
- 형식: `[타입] 설명` (예: `[기능] 사용자 인증 모듈 추가`)
- 타입: 기능, 수정, 리팩터, 문서, 테스트, 설정

## 테스트 규칙
- 새 기능은 반드시 단위 테스트를 포함한다
- UI 변경은 E2E 테스트(Playwright)로 검증한다
- 테스트 통과 전에는 기능을 완료로 표시하지 않는다

## 참조 문서
- 아키텍처: `docs/architecture.md`
- API 설계 원칙: `docs/api-design.md`
- 데이터베이스 스키마: `docs/database-schema.md`
- 품질 기준: `docs/quality-grades.md`
- 배포 절차: `docs/deployment.md`
```

### 3.4 업데이트 워크플로우

```
에이전트가 실수 발견
        │
        ▼
실수 유형 분류
        │
        ├─ 단순 규칙 위반 → CLAUDE.md에 금지 패턴 추가
        │
        ├─ 구조적 문제 → docs/architecture.md 업데이트
        │
        └─ 도구 부재 → 검증 스크립트 작성 (섹션 4 참조)
```

---

## 4. 구성요소 2: 결정론적 도구 및 검증

### 4.1 원칙

에이전트에게 "조심해라"라고 말하는 것은 효과가 없다. 올바른 행동을 **기계적으로 검증 가능하게** 만들어야 한다. 에이전트가 스스로 자기 작업을 확인할 수 있는 도구를 제공하는 것이 핵심이다.

### 4.2 필수 도구 체크리스트

| 카테고리 | 도구 | 목적 | 실행 시점 |
|----------|------|------|-----------|
| 코드 품질 | ESLint / Biome | 코딩 규칙 강제 | pre-commit |
| 타입 안전 | TypeScript strict mode | 타입 오류 차단 | 빌드 시 |
| 포매팅 | Prettier / dprint | 일관된 코드 스타일 | pre-commit |
| 단위 테스트 | Vitest / Jest | 로직 검증 | 기능 완료 시 |
| E2E 테스트 | Playwright / Puppeteer | UI 및 통합 검증 | PR 생성 시 |
| 아키텍처 검증 | 커스텀 린터 | 의존성 방향 강제 | CI 파이프라인 |
| 스크린샷 | Playwright screenshot | 시각적 결과 확인 | 에이전트 요청 시 |
| 번들 분석 | bundlesize / size-limit | 번들 크기 제한 | CI |

### 4.3 커스텀 검증 스크립트 예시

에이전트가 반복적으로 실패하는 영역에 대해 전용 검증 스크립트를 작성한다.

#### 의존성 방향 검증기

```bash
#!/bin/bash
# scripts/check-dependency-direction.sh
# domain 레이어가 infrastructure를 import하면 실패

VIOLATIONS=$(grep -rn "from.*infrastructure" src/domain/ 2>/dev/null)

if [ -n "$VIOLATIONS" ]; then
  echo "❌ 의존성 방향 위반 발견:"
  echo "$VIOLATIONS"
  echo ""
  echo "domain 레이어는 infrastructure를 직접 참조할 수 없습니다."
  echo "참조: docs/architecture.md#dependency-rules"
  exit 1
fi

echo "✅ 의존성 방향 검증 통과"
```

#### 금지 패턴 검사기

```bash
#!/bin/bash
# scripts/check-forbidden-patterns.sh

ERRORS=0

# console.log 검사 (테스트 파일 제외)
CONSOLE_LOGS=$(grep -rn "console\.log" src/ --include="*.ts" --include="*.tsx" \
  | grep -v "\.test\." | grep -v "\.spec\.")
if [ -n "$CONSOLE_LOGS" ]; then
  echo "❌ 프로덕션 코드에 console.log 발견:"
  echo "$CONSOLE_LOGS"
  ERRORS=$((ERRORS + 1))
fi

# any 타입 검사
ANY_TYPES=$(grep -rn ": any" src/ --include="*.ts" --include="*.tsx" \
  | grep -v "// eslint-disable" | grep -v "// any-허용")
if [ -n "$ANY_TYPES" ]; then
  echo "❌ any 타입 사용 발견:"
  echo "$ANY_TYPES"
  ERRORS=$((ERRORS + 1))
fi

if [ $ERRORS -gt 0 ]; then
  exit 1
fi

echo "✅ 금지 패턴 검사 통과"
```

### 4.4 에이전트 자가 검증 흐름

에이전트가 기능을 구현한 후 반드시 수행해야 하는 검증 순서를 CLAUDE.md에 명시한다.

```markdown
## 기능 완료 전 필수 검증 순서
1. `pnpm lint` 실행 → 오류 0건 확인
2. `pnpm typecheck` 실행 → 타입 오류 0건 확인
3. `pnpm test` 실행 → 관련 테스트 전체 통과 확인
4. `bash scripts/check-dependency-direction.sh` 실행
5. `bash scripts/check-forbidden-patterns.sh` 실행
6. 개발 서버 시작 후 브라우저에서 직접 확인 (해당 시)
7. 모든 검증 통과 후에만 커밋
```

---

## 5. 구성요소 3: 아키텍처 제약

### 5.1 원칙

에이전트는 제약 없는 환경에서 헤맨다. 명확한 아키텍처 제약은 에이전트가 **결정해야 할 것을 줄여주므로** 올바른 코드를 생성할 확률을 높인다. 인간 엔지니어 수백 명 규모에서나 필요하던 아키텍처 엄격성이, AI 에이전트와 협업할 때는 **초기부터 필수**가 된다.

### 5.2 레이어드 아키텍처 강제

```
프로젝트 루트
├── src/
│   ├── domain/           # 순수 비즈니스 로직 (외부 의존성 없음)
│   │   ├── entities/     # 엔티티 정의
│   │   ├── value-objects/ # 값 객체
│   │   └── services/     # 도메인 서비스
│   │
│   ├── application/      # 유스케이스, 오케스트레이션
│   │   ├── commands/     # 쓰기 작업
│   │   ├── queries/      # 읽기 작업
│   │   └── ports/        # 인터페이스 정의 (어댑터가 구현)
│   │
│   ├── infrastructure/   # 외부 시스템 연동
│   │   ├── database/     # DB 접근
│   │   ├── api-clients/  # 외부 API
│   │   └── adapters/     # 포트 구현체
│   │
│   └── presentation/     # UI, API 엔드포인트
│       ├── components/   # UI 컴포넌트
│       ├── pages/        # 페이지/라우트
│       └── api/          # REST/GraphQL 핸들러
│
├── docs/                 # 하네스 문서 (에이전트용 지식 기반)
├── scripts/              # 검증 스크립트
├── tests/                # 테스트 (단위, 통합, E2E)
└── CLAUDE.md             # 에이전트 진입점
```

### 5.3 의존성 방향 규칙

```
domain ← application ← infrastructure
                     ← presentation

규칙:
- domain은 다른 레이어를 알지 못한다
- application은 domain만 참조한다
- infrastructure는 application의 포트(인터페이스)를 구현한다
- presentation은 application을 호출한다
- 횡단 관심사(인증, 로깅, 피처 플래그)는 단일 Providers 인터페이스를 통해 진입
```

### 5.4 파일 및 모듈 제약

CLAUDE.md에 명시할 아키텍처 제약 예시:

```markdown
## 아키텍처 제약 (기계적으로 강제됨)
- 단일 파일은 300줄을 초과할 수 없다 (초과 시 분리)
- 단일 함수는 50줄을 초과할 수 없다
- 컴포넌트 props는 최대 7개 (초과 시 객체로 묶기)
- 순환 의존성 금지 (madge로 검증)
- barrel export(index.ts) 사용 시 해당 모듈의 public API만 노출
- 새 패키지 추가 시 반드시 docs/dependencies.md에 사유 기록
```

### 5.5 네이밍 컨벤션

```markdown
## 네이밍 규칙
- 파일명: kebab-case (예: user-profile.tsx)
- 컴포넌트명: PascalCase (예: UserProfile)
- 함수명: camelCase (예: getUserProfile)
- 상수: SCREAMING_SNAKE_CASE (예: MAX_RETRY_COUNT)
- 타입/인터페이스: PascalCase, I 접두사 금지 (예: UserProfile, 아님: IUserProfile)
- 테스트 파일: [대상].test.ts (예: user-profile.test.ts)
- 훅: use 접두사 (예: useUserProfile)
```

---

## 6. 구성요소 4: 피드백 루프 및 관찰

### 6.1 원칙

에이전트는 기존 코드베이스의 패턴을 복제하는데, 시간이 지나면 최적이 아닌 패턴도 누적된다. 이를 **자동으로 감지하고 정리하는 메커니즘**이 필수다.

### 6.2 진행 추적 파일 (claude-progress.txt)

장기 작업 시 세션 간 연속성을 유지하기 위한 파일이다. Anthropic의 장기 실행 에이전트 연구에서 검증된 패턴이다.

```markdown
# claude-progress.txt 템플릿

## 현재 상태
- 마지막 작업 세션: [날짜/시간]
- 현재 진행 중인 기능: [기능명]
- 전체 진행률: [완료 기능 수]/[전체 기능 수]

## 최근 완료된 작업
- [날짜] [기능명] - [커밋 해시]
- [날짜] [기능명] - [커밋 해시]

## 진행 중 작업
- [기능명]: [상태 설명]
  - 완료: [완료된 부분]
  - 남은 작업: [남은 부분]
  - 차단 요소: [있으면 기술]

## 다음 우선순위
1. [기능명] - [사유]
2. [기능명] - [사유]

## 알려진 문제
- [문제 설명] - [임시 해결책 또는 TODO]

## 이번 세션에서 추가/변경된 파일
- [파일 경로]: [변경 사유]
```

### 6.3 기능 목록 파일 (feature-list.json)

Anthropic 연구에서 JSON 형식이 Markdown보다 모델의 부적절한 수정에 강건하다고 확인되었다.

```json
{
  "features": [
    {
      "id": "auth-001",
      "name": "이메일 기반 사용자 인증",
      "status": "completed",
      "priority": 1,
      "acceptance_criteria": [
        "이메일/비밀번호로 회원가입 가능",
        "이메일/비밀번호로 로그인 가능",
        "JWT 토큰 발급 및 검증",
        "비밀번호 해싱 (bcrypt)"
      ],
      "test_coverage": true,
      "commit": "a1b2c3d"
    },
    {
      "id": "auth-002",
      "name": "소셜 로그인 (Google OAuth)",
      "status": "in-progress",
      "priority": 2,
      "acceptance_criteria": [
        "Google OAuth 2.0 플로우 구현",
        "기존 계정과 연동",
        "프로필 정보 자동 채움"
      ],
      "test_coverage": false,
      "commit": null
    },
    {
      "id": "profile-001",
      "name": "사용자 프로필 관리",
      "status": "pending",
      "priority": 3,
      "acceptance_criteria": [
        "프로필 조회",
        "프로필 수정 (이름, 아바타)",
        "비밀번호 변경"
      ],
      "test_coverage": false,
      "commit": null
    }
  ],
  "metadata": {
    "total": 3,
    "completed": 1,
    "in_progress": 1,
    "pending": 1,
    "last_updated": "2026-03-19"
  }
}
```

### 6.4 품질 등급 추적

프로젝트의 각 도메인과 아키텍처 레이어에 대해 품질 등급을 추적한다.

```markdown
# docs/quality-grades.md

## 도메인별 품질 등급

| 도메인 | 코드 품질 | 테스트 커버리지 | 문서화 | 종합 |
|--------|-----------|----------------|--------|------|
| 인증   | A         | 92%            | B      | A-   |
| 프로필 | B         | 65%            | C      | B-   |
| 결제   | C         | 40%            | D      | C-   |

## 등급 기준
- A: 린트 경고 0, 커버리지 90%+, 설계 문서 최신
- B: 린트 경고 5개 이하, 커버리지 70%+, 설계 문서 존재
- C: 린트 경고 10개 이하, 커버리지 50%+, 설계 문서 불완전
- D: 기준 미달, 우선 개선 필요

## 갭 및 개선 계획
- 결제 도메인: 테스트 커버리지 40% → 70% 목표, 스프린트 12에서 집중 작업
- 프로필 도메인: API 설계 문서 부재 → docs/api-design-profile.md 작성 필요
```

### 6.5 AI 드리프트 방지: 가비지 컬렉션

에이전트가 누적하는 기술 부채를 정기적으로 정리하는 절차다.

```markdown
## 주간 코드 정리 절차 (금요일)

### 자동 감지
1. `pnpm lint --max-warnings 0` 으로 새로 발생한 경고 확인
2. `npx madge --circular src/` 로 순환 의존성 확인
3. `npx ts-prune` 로 미사용 export 확인
4. 번들 크기 변화 추적: 이전 대비 10% 이상 증가 시 조사

### 수동 검토
1. 최근 PR에서 반복되는 패턴 확인
2. 복붙된 코드 블록 식별 → 공통 유틸로 추출
3. CLAUDE.md 규칙 중 더 이상 유효하지 않은 항목 제거
4. docs/ 문서와 실제 코드의 불일치 확인

### 정리 에이전트 태스크
에이전트에게 정리 작업을 위임할 때 사용하는 프롬프트:

> 이번 주에 머지된 PR들을 검토하고, 다음을 수행하라:
> 1. 중복 코드를 식별하여 공통 유틸로 추출
> 2. 미사용 import와 export를 제거
> 3. 타입 정의가 누락된 곳에 타입을 추가
> 4. 변경 사항에 대한 테스트가 누락된 경우 테스트 추가
> 5. 변경 내용을 claude-progress.txt에 기록
```

---

## 7. 세션 관리 프로토콜

### 7.1 세션 시작 루틴

에이전트가 새 세션을 시작할 때 반드시 수행해야 하는 절차를 CLAUDE.md에 명시한다.

```markdown
## 세션 시작 절차 (필수)
1. `pwd` 로 현재 위치 확인
2. `git log --oneline -10` 으로 최근 작업 내역 확인
3. `cat claude-progress.txt` 로 진행 상태 파악
4. `cat feature-list.json | jq '.features[] | select(.status != "completed")'` 로 미완료 기능 확인
5. 개발 서버 시작: `pnpm dev`
6. 기본 스모크 테스트: `pnpm test --run`
7. 가장 높은 우선순위의 미완료 기능 선택
8. 작업 시작 전 계획을 claude-progress.txt에 기록
```

### 7.2 세션 종료 루틴

```markdown
## 세션 종료 절차 (필수)
1. 현재 작업을 커밋 가능한 상태로 정리
2. 모든 검증 스크립트 실행 및 통과 확인
3. 설명적인 커밋 메시지와 함께 커밋
4. claude-progress.txt 업데이트:
   - 완료한 작업
   - 진행 중인 작업의 현재 상태
   - 다음 세션에서 해야 할 작업
   - 발견한 문제점이나 차단 요소
5. feature-list.json 상태 업데이트
6. 미완료 작업이 있다면 TODO 주석으로 표시
```

### 7.3 이니셜라이저-코딩 에이전트 패턴

장기 프로젝트에서 Anthropic이 검증한 이중 에이전트 패턴이다.

**이니셜라이저 에이전트** (첫 번째 세션에서만 실행):
- 프로젝트 구조 생성
- feature-list.json 작성 (고수준 요구사항을 수백 개의 구체적 기능으로 확장)
- init.sh 스크립트 작성 (개발 서버 시작 방법)
- claude-progress.txt 초기화
- 첫 번째 git commit
- CLAUDE.md 작성

**코딩 에이전트** (이후 모든 세션):
- 세션 시작 루틴 실행
- 한 번에 하나의 기능만 구현
- 기능 완료 후 테스트 작성 및 실행
- 커밋 후 진행 파일 업데이트
- 절대로 "전체를 한번에" 완성하려 하지 않음

---

## 8. 실패 패턴과 대응 전략

### 8.1 에이전트의 공통 실패 모드

| 실패 패턴 | 증상 | 하네스 대응 |
|-----------|------|-------------|
| 원샷 시도 | 전체 앱을 한번에 만들려 함 | feature-list.json으로 작업 단위 강제 분할 |
| 조기 완료 선언 | 테스트 없이 "완료" 주장 | 검증 스크립트 통과를 완료 조건에 포함 |
| 패턴 드리프트 | 기존 나쁜 패턴을 복제 | 주간 가비지 컬렉션 + 아키텍처 린터 |
| 컨텍스트 유실 | 이전 세션 작업을 모름 | claude-progress.txt + git log |
| 환각 API 호출 | 존재하지 않는 API 사용 | docs/에 API 명세 유지, 린터로 import 검증 |
| 과잉 엔지니어링 | 불필요한 추상화 추가 | CLAUDE.md에 "YAGNI 원칙 준수" 명시 |
| 테스트 회피 | 테스트 작성을 건너뜀 | CI에서 커버리지 임계값 강제 |
| 보안 무시 | 비밀키 하드코딩, SQL 인젝션 | 보안 린터 + 금지 패턴 검사 |

### 8.2 실패 → 하네스 개선 워크플로우

```
에이전트 실패 발견
        │
        ▼
근본 원인 분석 ─────────────────────────────────────┐
        │                                            │
        ▼                                            │
"이 실패를 어떤 메커니즘이 방지할 수 있었는가?"       │
        │                                            │
        ├─ 규칙으로 방지 가능?                        │
        │   → CLAUDE.md 업데이트                      │
        │                                            │
        ├─ 자동 검사로 방지 가능?                      │
        │   → 검증 스크립트 / 린터 규칙 추가           │
        │                                            │
        ├─ 구조적 제약으로 방지 가능?                   │
        │   → 아키텍처 규칙 추가, 디렉토리 구조 변경    │
        │                                            │
        └─ 더 나은 컨텍스트로 방지 가능?               │
            → docs/ 문서 추가 또는 업데이트             │
                                                      │
        하네스 개선 완료 ◄────────────────────────────┘
        │
        ▼
    동일 실패 재발 방지 확인
```

---

## 9. docs/ 디렉토리 구조 (지식 기반)

```
docs/
├── architecture.md          # 시스템 아키텍처 전체 지도
├── api-design.md            # API 설계 원칙 및 규칙
├── database-schema.md       # DB 스키마 및 마이그레이션 규칙
├── quality-grades.md        # 도메인별 품질 등급 추적
├── dependencies.md          # 외부 패키지 사용 사유 기록
├── deployment.md            # 배포 절차 및 환경 설정
├── security.md              # 보안 규칙 및 체크리스트
├── testing-strategy.md      # 테스트 전략 및 작성 가이드
├── error-handling.md        # 에러 처리 규칙
├── design/                  # 기능별 설계 문서
│   ├── auth-design.md
│   ├── payment-design.md
│   └── ...
└── adr/                     # 아키텍처 결정 기록 (Architecture Decision Records)
    ├── 001-framework-selection.md
    ├── 002-database-choice.md
    └── ...
```

각 문서는 에이전트가 참조할 수 있는 **시스템 오브 레코드(system of record)** 역할을 한다. CLAUDE.md가 목차라면, docs/의 각 문서가 본문이다.

### 9.1 ADR (Architecture Decision Record) 템플릿

에이전트가 "왜 이렇게 했는가"를 이해하는 데 핵심적인 문서다.

```markdown
# ADR-[번호]: [결정 제목]

## 상태
[제안됨 | 승인됨 | 폐기됨 | 대체됨(→ ADR-XX)]

## 맥락
이 결정이 필요한 배경과 제약 조건

## 결정
무엇을 결정했는가

## 근거
왜 이 결정을 내렸는가. 검토한 대안과 각각의 장단점

## 결과
이 결정으로 인해 발생하는 영향. 에이전트가 알아야 할 제약
```

---

## 10. CI/CD 파이프라인 통합

### 10.1 에이전트 친화적 CI 구성

```yaml
# .github/workflows/agent-ci.yml
name: Agent CI

on:
  pull_request:
    branches: [main, develop]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup
        uses: actions/setup-node@v4
        with:
          node-version: 20

      - name: Install
        run: pnpm install --frozen-lockfile

      - name: Lint
        run: pnpm lint --max-warnings 0

      - name: Type Check
        run: pnpm typecheck

      - name: Forbidden Patterns
        run: bash scripts/check-forbidden-patterns.sh

      - name: Dependency Direction
        run: bash scripts/check-dependency-direction.sh

      - name: Circular Dependencies
        run: npx madge --circular src/

      - name: Unit Tests
        run: pnpm test --coverage
        env:
          MIN_COVERAGE: 70

      - name: E2E Tests
        run: pnpm test:e2e

      - name: Bundle Size
        run: npx size-limit
```

### 10.2 PR 자동 검증

에이전트가 생성한 PR에 대해 자동 피드백을 제공하여, 에이전트가 스스로 수정할 수 있게 한다.

```markdown
## PR 제출 규칙 (CLAUDE.md에 추가)
- PR 제목: `[타입] 설명` 형식
- PR 본문: 변경 사항 요약, 테스트 방법, 관련 기능 ID
- CI 전체 통과 필수
- 새 기능 시 feature-list.json 상태 업데이트 포함
- 300줄 초과 변경 금지 (초과 시 PR 분할)
```

---

## 11. 하네스 성숙도 모델

### 11.1 5단계 성숙도

| 단계 | 이름 | 설명 | 핵심 지표 |
|------|------|------|-----------|
| L1 | 기초 | CLAUDE.md 존재, 기본 빌드/테스트 명령어 기록 | 에이전트가 프로젝트를 빌드할 수 있음 |
| L2 | 규칙 기반 | 코딩 규칙, 금지 패턴, 네이밍 컨벤션 명시 | 린트 통과율 95%+ |
| L3 | 검증 기반 | 커스텀 검증 스크립트, 아키텍처 린터 운용 | 에이전트 PR의 CI 통과율 80%+ |
| L4 | 자동화 | 피드백 루프, 진행 추적, 가비지 컬렉션 운용 | 장기 멀티세션 작업 가능 |
| L5 | 자율 | 에이전트가 end-to-end로 기능 개발 가능 | 인간 개입 최소화, 드리프트 자동 감지 |

### 11.2 단계별 도입 로드맵

**1주차 (L1 → L2)**:
- CLAUDE.md 작성
- 기본 빌드/테스트/린트 명령어 정리
- 코딩 규칙과 금지 패턴 초기 목록 작성
- pre-commit 훅 설정 (린트 + 포매팅)

**2~3주차 (L2 → L3)**:
- 에이전트 실패 패턴 수집 시작
- 커스텀 검증 스크립트 첫 번째 세트 작성
- 아키텍처 의존성 방향 린터 도입
- CI 파이프라인에 모든 검증 통합

**4~6주차 (L3 → L4)**:
- claude-progress.txt 도입
- feature-list.json 도입
- 주간 가비지 컬렉션 프로세스 시작
- docs/ 지식 기반 체계적 구축
- 품질 등급 추적 시작

**7주차 이후 (L4 → L5)**:
- 이니셜라이저-코딩 에이전트 패턴 적용
- 에이전트 자율성 점진적 확대
- 관찰 가능성 스택 연동 (로그, 메트릭, 트레이스)
- 에이전트가 직접 docs/ 업데이트하는 워크플로우 도입

---

## 12. 실전 체크리스트

### 12.1 프로젝트 시작 시 체크리스트

```
□ CLAUDE.md 작성 완료
□ 프로젝트 구조 결정 및 디렉토리 생성
□ 빌드/테스트/린트 명령어 확인 및 기록
□ pre-commit 훅 설정 (린트 + 포매팅 + 타입체크)
□ .gitignore 설정
□ docs/ 디렉토리 생성 및 architecture.md 초안 작성
□ feature-list.json 초기 작성
□ claude-progress.txt 초기화
□ CI 파이프라인 기본 구성
□ 첫 번째 기능을 에이전트에게 할당하여 하네스 동작 확인
```

### 12.2 일일 운영 체크리스트

```
□ 에이전트 세션 시작 시 세션 시작 루틴 수행 확인
□ 에이전트가 한 번에 하나의 기능만 작업하는지 확인
□ 커밋 전 모든 검증 통과 확인
□ claude-progress.txt 업데이트 확인
□ 새로운 에이전트 실패 패턴 발견 시 즉시 하네스 업데이트
```

### 12.3 주간 유지보수 체크리스트

```
□ CLAUDE.md 규칙 검토: 불필요한 규칙 제거, 누락된 규칙 추가
□ docs/ 문서와 실제 코드 불일치 확인
□ 품질 등급 업데이트
□ 에이전트 PR 분석: 반복 실패 패턴 식별
□ 검증 스크립트 효과성 점검
□ 코드 정리(가비지 컬렉션) 수행
□ feature-list.json 우선순위 재조정
```

---

## 13. 부록

### 13.1 참조 자료

| 자료 | 출처 | 핵심 기여 |
|------|------|-----------|
| My AI Adoption Journey | Mitchell Hashimoto (2026.02) | "하네스 엔지니어링" 용어 명명, 6단계 채택 여정 |
| Harness engineering: leveraging Codex | OpenAI (2026.02) | 100만 라인 실험, AGENTS.md 설계 |
| Effective harnesses for long-running agents | Anthropic (2025.11) | 이니셜라이저/코딩 에이전트 패턴, claude-progress.txt |
| Exploring Gen AI: Harness Engineering | Birgitta Böckeler / Thoughtworks (2026.02) | 결정론적 도구 + 컨텍스트 + 가비지 컬렉션 3축 분석 |
| Skill Issue: Harness Engineering | HumanLayer (2026.03) | 하네스 = 컨텍스트 엔지니어링의 부분집합 프레이밍 |

### 13.2 용어 정의

| 용어 | 정의 |
|------|------|
| 하네스 (Harness) | AI 에이전트를 둘러싼 제약, 도구, 문서, 피드백 루프의 총합 |
| 하네스 엔지니어링 | 에이전트가 안정적으로 작업하도록 하네스를 설계·유지하는 엔지니어링 분야 |
| 컨텍스트 엔지니어링 | 에이전트의 컨텍스트 윈도우에 주입되는 정보를 체계적으로 설계하는 기법 |
| 프롬프트 엔지니어링 | 입력 텍스트를 최적화하여 모델 출력을 개선하는 기법 |
| AGENTS.md / CLAUDE.md | 에이전트가 세션 시작 시 읽는 프로젝트 지침 파일 |
| 이니셜라이저 에이전트 | 프로젝트 첫 세션에서 환경을 설정하는 전용 에이전트 |
| 코딩 에이전트 | 이후 세션에서 기능을 점진적으로 구현하는 에이전트 |
| 가비지 컬렉션 | 에이전트가 누적한 기술 부채를 정기적으로 정리하는 절차 |
| 드리프트 | 시간이 지남에 따라 코드가 의도한 아키텍처에서 벗어나는 현상 |
| 백프레셔 | 에이전트의 작업 속도를 제어하여 품질을 유지하는 메커니즘 |

### 13.3 이 문서의 업데이트 규칙

이 문서 자체도 하네스의 일부이므로, 다음 규칙을 따른다:

1. 새로운 에이전트 실패 패턴이 기존 카테고리에 해당하면 해당 섹션에 추가
2. 새로운 카테고리의 실패가 발견되면 섹션 8의 테이블에 행 추가
3. 분기(3개월)마다 전체 문서를 검토하여 더 이상 유효하지 않은 내용 제거
4. 외부 참조 자료가 업데이트되면 부록 갱신

---

> **이 프레임워크의 핵심을 한 문장으로**: 코드를 쓰는 것은 에이전트에게, 코드가 올바르게 쓰여지는 환경을 만드는 것은 엔지니어에게.
