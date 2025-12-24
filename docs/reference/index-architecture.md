# `/sc:index` 동작 방법과 원리

## 개요

`/sc:index`는 프로젝트의 포괄적인 문서화와 지식 베이스를 생성하는 고급 명령입니다. `/sc:index-repo`가 단순 인덱싱에 집중하는 반면, `/sc:index`는 **다양한 문서 타입 생성**, **MCP 서버 통합**, **멀티 페르소나 협업**을 통해 전문적인 문서화를 수행합니다.

## `/sc:index` vs `/sc:index-repo` 비교

| 특징 | `/sc:index` | `/sc:index-repo` |
| ------ | ----------- | ---------------- |
| **목적** | 포괄적 문서화 및 지식 베이스 생성 | 저장소 인덱싱 (토큰 절감) |
| **출력** | 다양한 문서 타입 (API, 구조, README 등) | PROJECT_INDEX.md + JSON |
| **MCP 통합** | Sequential, Context7 | 없음 |
| **페르소나** | Architect, Scribe, Quality | 없음 |
| **복잡도** | 높음 (체계적 분석) | 낮음 (메타데이터 추출) |
| **용도** | 문서화 프로젝트 | 컨텍스트 최적화 |

## 아키텍처 개요

```
사용자 입력: /sc:index [target] [--type docs|api|structure|readme]
    ↓
Claude Code가 명령 파일 읽기
    ↓
~/.claude/commands/sc/index.md
    ↓
MCP 서버 활성화 (Sequential, Context7)
    ↓
멀티 페르소나 협업 시작
    ↓
5단계 행동 흐름 실행
    ↓
문서 생성 및 검증
```

## 1. 명령 설치 및 구조

### 1.1 명령 파일 위치

**소스 위치**:
- `src/superclaude/commands/index.md` (패키지 배포용)
- `plugins/superclaude/commands/index.md` (개발용)

**설치 위치**:
- `~/.claude/commands/sc/index.md` (사용자 시스템)

### 1.2 명령 메타데이터

```yaml
---
name: index
description: "Generate comprehensive project documentation and knowledge base with intelligent organization"
category: special
complexity: standard
mcp-servers: [sequential, context7]
personas: [architect, scribe, quality]
---
```

**핵심 특징**:
- **category: special**: 특수 목적 명령
- **MCP 통합**: Sequential, Context7 자동 활성화
- **멀티 페르소나**: Architect, Scribe, Quality 협업

### 1.3 사용법

```
/sc:index [target] [--type docs|api|structure|readme] [--format md|json|yaml]
```

**파라미터**:
- `target`: 문서화할 대상 (디렉토리 또는 파일)
- `--type`: 문서 타입 선택
  - `docs`: 일반 문서화
  - `api`: API 문서
  - `structure`: 프로젝트 구조 문서
  - `readme`: README 생성
- `--format`: 출력 형식
  - `md`: Markdown (기본값)
  - `json`: JSON 형식
  - `yaml`: YAML 형식

## 2. MCP 서버 통합

### 2.1 Sequential MCP

**목적**: 복잡한 다단계 프로젝트 분석 및 체계적 문서 생성

**활용 시점**:
- 프로젝트 구조가 복잡한 경우 (3개 이상의 상호 연결된 컴포넌트)
- 체계적 분석이 필요한 경우
- 다단계 문서 생성 워크플로우

**기능**:
- 구조화된 다단계 추론
- 가설 테스트 및 검증
- 증거 기반 분석
- 체계적 문제 해결

**예시**:
```
[Sequential MCP] 프로젝트 구조 분석
  → Phase 1: 컴포넌트 식별
  → Phase 2: 의존성 매핑
  → Phase 3: 문서 구조 설계
  → Phase 4: 검증 및 개선
```

### 2.2 Context7 MCP

**목적**: 프레임워크별 문서 패턴 및 공식 표준 제공

**활용 시점**:
- 특정 프레임워크/라이브러리 사용 시
- 공식 문서 패턴 적용 필요 시
- 업계 표준 준수 필요 시

**기능**:
- 공식 문서 패턴 조회
- 프레임워크별 베스트 프랙티스
- 표준 문서 구조 제공
- 일관성 검증

**예시**:
```
[Context7 MCP] React 프로젝트 문서화
  → React 공식 문서 패턴 조회
  → 컴포넌트 문서 표준 적용
  → API 문서 구조 생성
```

### 2.3 MCP 통합 워크플로우

```
[사용자] /sc:index src/api --type api
    ↓
[Claude Code] 명령 파일 로드
    ↓
[MCP 활성화] Sequential + Context7
    ↓
[Sequential] 체계적 분석 시작
  ├─ Phase 1: API 엔드포인트 식별
  ├─ Phase 2: 파라미터 및 응답 분석
  └─ Phase 3: 문서 구조 설계
    ↓
[Context7] 프레임워크 패턴 조회
  ├─ API 문서 표준 확인
  ├─ 예제 패턴 가져오기
  └─ 베스트 프랙티스 적용
    ↓
[페르소나 협업] 문서 생성
    ↓
[결과] API 문서 생성 완료
```

## 3. 멀티 페르소나 협업

### 3.1 System Architect (Architect)

**역할**: 구조 설계 및 아키텍처 문서화

**책임**:
- 프로젝트 구조 분석
- 컴포넌트 경계 정의
- 의존성 매핑
- 아키텍처 결정 문서화

**출력**:
- 아키텍처 다이어그램
- 시스템 컴포넌트 문서
- 의존성 그래프
- 확장성 계획

**행동 원칙**:
- 10배 성장을 고려한 설계
- 느슨한 결합 및 명확한 경계
- 장기적 유지보수성 우선

### 3.2 Technical Writer (Scribe)

**역할**: 콘텐츠 작성 및 문서 품질 관리

**책임**:
- 명확하고 포괄적인 문서 작성
- 대상 독자 분석
- 실용적인 예제 제공
- 접근성 표준 준수

**출력**:
- API 문서
- 사용자 가이드
- 기술 명세서
- 설치 문서

**행동 원칙**:
- 독자 중심 작성
- 명확성 우선
- 작동하는 예제 포함
- 스캔 가능한 구조

### 3.3 Quality Engineer (Quality)

**역할**: 문서 품질 검증 및 완전성 평가

**책임**:
- 문서 완전성 평가
- 정확성 검증
- 표준 준수 확인
- 유지보수 계획 수립

**출력**:
- 품질 평가 보고서
- 검증 체크리스트
- 개선 제안
- 표준 준수 확인

**행동 원칙**:
- 체계적 검증
- 위험 기반 우선순위
- 측정 가능한 결과
- 지속적 개선

### 3.4 페르소나 협업 흐름

```
[Phase 1: 분석]
Architect → 프로젝트 구조 분석
  ↓
[Phase 2: 설계]
Architect → 문서 구조 설계
Scribe → 콘텐츠 구조 계획
  ↓
[Phase 3: 생성]
Scribe → 문서 작성
Architect → 아키텍처 다이어그램 추가
  ↓
[Phase 4: 검증]
Quality → 완전성 평가
Quality → 정확성 검증
  ↓
[Phase 5: 유지보수]
Scribe → 업데이트 계획
Quality → 품질 모니터링
```

## 4. 5단계 행동 흐름

### Phase 1: Analyze (분석)

**목적**: 프로젝트 구조 검토 및 핵심 문서 구성 요소 식별

**활동**:
- 프로젝트 디렉토리 구조 탐색
- 주요 모듈 및 컴포넌트 식별
- 진입점(Entry Points) 탐지
- 의존성 관계 분석

**도구 활용**:
- `Read/Grep/Glob`: 프로젝트 구조 분석
- `Sequential MCP`: 체계적 분석
- `Context7 MCP`: 프레임워크 패턴 확인

**출력**:
- 프로젝트 구조 맵
- 핵심 컴포넌트 목록
- 의존성 그래프
- 문서화 우선순위

### Phase 2: Organize (조직화)

**목적**: 지능적 조직 패턴 및 크로스 레퍼런싱 전략 적용

**활동**:
- 정보 아키텍처 설계
- 논리적 계층 구조 생성
- 크로스 레퍼런스 링크 생성
- 탐색 경로 최적화

**도구 활용**:
- `Architect Persona`: 구조 설계
- `Scribe Persona`: 콘텐츠 조직
- `Context7 MCP`: 표준 구조 패턴

**출력**:
- 문서 구조 계층
- 크로스 레퍼런스 맵
- 탐색 인덱스
- 네비게이션 가이드

### Phase 3: Generate (생성)

**목적**: 프레임워크별 패턴을 적용한 포괄적 문서 생성

**활동**:
- 문서 타입별 템플릿 적용
- 프레임워크 패턴 통합
- 예제 코드 생성
- 다이어그램 및 시각화 추가

**도구 활용**:
- `Scribe Persona`: 문서 작성
- `Architect Persona`: 다이어그램 생성
- `Context7 MCP`: 패턴 적용
- `Write`: 파일 생성

**출력**:
- Markdown/JSON/YAML 문서
- API 문서
- 구조 문서
- README 파일

### Phase 4: Validate (검증)

**목적**: 문서 완전성 및 품질 표준 보장

**활동**:
- 완전성 평가
- 정확성 검증
- 표준 준수 확인
- 접근성 검사

**도구 활용**:
- `Quality Persona`: 품질 검증
- `Sequential MCP`: 체계적 검증
- `TodoWrite`: 검증 체크리스트

**출력**:
- 품질 평가 보고서
- 검증 체크리스트
- 개선 제안
- 표준 준수 확인서

### Phase 5: Maintain (유지보수)

**목적**: 기존 문서 업데이트 및 수동 추가 사항 보존

**활동**:
- 기존 문서 분석
- 변경사항 감지
- 수동 추가 사항 보존
- 자동 업데이트 계획

**도구 활용**:
- `Scribe Persona`: 업데이트 계획
- `Quality Persona`: 변경 영향 평가
- `Read`: 기존 문서 분석

**출력**:
- 업데이트 계획
- 변경 로그
- 보존된 사용자 편집
- 유지보수 가이드

## 5. 문서 타입별 상세

### 5.1 API 문서 (`--type api`)

**대상**: API 엔드포인트, 함수, 클래스

**생성 내용**:
- 엔드포인트 목록
- 파라미터 설명
- 응답 형식
- 예제 코드
- 에러 처리

**페르소나 역할**:
- **Architect**: API 구조 분석
- **Scribe**: 문서 작성
- **Quality**: 완전성 검증

**출력 예시**:
```markdown
# API Documentation

## Endpoints

### GET /api/users
**Description**: Retrieve user list
**Parameters**:
- `page` (int): Page number
- `limit` (int): Items per page

**Response**:
```json
{
  "users": [...],
  "total": 100
}
```

**Example**:
```python
response = requests.get('/api/users', params={'page': 1, 'limit': 10})
```
```

### 5.2 구조 문서 (`--type structure`)

**대상**: 프로젝트 디렉토리 구조, 모듈 계층

**생성 내용**:
- 디렉토리 트리
- 모듈 설명
- 컴포넌트 관계
- 의존성 그래프

**페르소나 역할**:
- **Architect**: 구조 분석 및 다이어그램
- **Scribe**: 설명 작성
- **Quality**: 구조 검증

**출력 예시**:
```markdown
# Project Structure

```
project/
├── src/
│   ├── api/          # API endpoints
│   ├── models/       # Data models
│   └── utils/        # Utility functions
├── tests/            # Test suites
└── docs/             # Documentation
```

## Components

### api/
**Purpose**: API endpoint handlers
**Dependencies**: models/, utils/
**Exports**: Router, handlers
```

### 5.3 일반 문서 (`--type docs`)

**대상**: 전체 프로젝트 문서화

**생성 내용**:
- 프로젝트 개요
- 설치 가이드
- 사용 가이드
- 아키텍처 설명
- 기여 가이드

**페르소나 역할**:
- **Architect**: 아키텍처 문서
- **Scribe**: 사용자 가이드
- **Quality**: 문서 품질 관리

### 5.4 README (`--type readme`)

**대상**: 프로젝트 루트 README

**생성 내용**:
- 프로젝트 소개
- 빠른 시작 가이드
- 주요 기능
- 설치 방법
- 사용 예제

**페르소나 역할**:
- **Scribe**: README 작성 (주도)
- **Architect**: 구조 정보 제공
- **Quality**: 완전성 검증

## 6. 도구 조정 (Tool Coordination)

### 6.1 분석 도구

**Read/Grep/Glob**:
- 프로젝트 구조 분석
- 문서 생성용 콘텐츠 추출
- 패턴 검색

**활용 예시**:
```
[Glob] src/**/*.py → 모든 Python 파일 찾기
[Grep] def.*api → API 함수 식별
[Read] main.py → 진입점 분석
```

### 6.2 생성 도구

**Write**:
- 문서 파일 생성
- 지능적 조직화
- 크로스 레퍼런싱

**활용 예시**:
```
[Write] docs/api.md → API 문서 생성
[Write] docs/structure.md → 구조 문서 생성
[Write] README.md → README 업데이트
```

### 6.3 추적 도구

**TodoWrite**:
- 복잡한 다중 컴포넌트 문서 워크플로우 진행 추적
- 단계별 작업 관리

**활용 예시**:
```
[TodoWrite] 문서화 작업 목록 생성
  - [ ] API 엔드포인트 분석
  - [ ] 문서 구조 설계
  - [ ] 콘텐츠 작성
  - [ ] 품질 검증
```

### 6.4 위임 도구

**Task**:
- 대규모 문서화 작업의 체계적 조정
- 하위 작업 위임

**활용 예시**:
```
[Task] 대규모 프로젝트 문서화
  → Task 1: API 문서 생성
  → Task 2: 구조 문서 생성
  → Task 3: 사용자 가이드 작성
```

## 7. 실제 실행 예시

### 7.1 API 문서 생성

```
[사용자] /sc:index src/api --type api --format md
    ↓
[Claude Code] 명령 파일 로드
    ↓
[MCP 활성화] Sequential + Context7
    ↓
[Sequential] 체계적 분석
  Phase 1: API 엔드포인트 식별
    → [Glob] src/api/**/*.py
    → [Grep] @app.route|def.*api
    → [Read] 주요 엔드포인트 파일
  Phase 2: 파라미터 분석
    → [Grep] request\.(get|post|json)
    → [Read] 요청 처리 로직
  Phase 3: 응답 형식 분석
    → [Grep] return|jsonify
    → [Read] 응답 구조
    ↓
[Context7] 프레임워크 패턴 조회
  → Flask API 문서 표준 확인
  → 예제 패턴 가져오기
    ↓
[페르소나 협업]
  Architect → API 구조 다이어그램
  Scribe → 문서 작성
  Quality → 완전성 검증
    ↓
[Write] docs/api.md 생성
    ↓
[결과] API 문서 생성 완료
```

### 7.2 프로젝트 구조 문서 생성

```
[사용자] /sc:index . --type structure
    ↓
[Claude Code] 명령 파일 로드
    ↓
[MCP 활성화] Sequential + Context7
    ↓
[Sequential] 체계적 분석
  Phase 1: 디렉토리 구조 탐색
    → [Glob] **/*
    → [Read] 주요 디렉토리
  Phase 2: 모듈 관계 분석
    → [Grep] import|from
    → [Read] 의존성 파일
  Phase 3: 컴포넌트 식별
    → [Glob] src/**/*.py
    → [Read] 주요 모듈
    ↓
[Context7] 프로젝트 구조 패턴 확인
    ↓
[페르소나 협업]
  Architect → 구조 다이어그램 및 의존성 그래프
  Scribe → 설명 및 문서 작성
  Quality → 구조 검증
    ↓
[Write] docs/structure.md 생성
    ↓
[결과] 구조 문서 생성 완료
```

## 8. 주요 패턴

### 8.1 구조 분석 패턴

```
프로젝트 검토 → 컴포넌트 식별 → 논리적 조직 → 크로스 레퍼런싱
```

**단계**:
1. 프로젝트 전체 구조 탐색
2. 주요 컴포넌트 및 모듈 식별
3. 논리적 그룹화 및 계층 구조 생성
4. 컴포넌트 간 관계 문서화
5. 크로스 레퍼런스 링크 생성

### 8.2 문서 타입 패턴

```
API 문서 → 구조 문서 → README → 지식 베이스 접근
```

**특징**:
- 각 문서 타입은 특정 목적에 최적화
- 타입 간 상호 참조 가능
- 통합 지식 베이스 구성

### 8.3 품질 검증 패턴

```
완전성 평가 → 정확성 검증 → 표준 준수 → 유지보수 계획
```

**체크리스트**:
- [ ] 모든 주요 컴포넌트 문서화
- [ ] 예제 코드 작동 확인
- [ ] 표준 형식 준수
- [ ] 접근성 요구사항 충족
- [ ] 업데이트 계획 수립

### 8.4 프레임워크 통합 패턴

```
Context7 패턴 → 공식 표준 → 베스트 프랙티스 → 일관성 검증
```

**프로세스**:
1. Context7에서 프레임워크 패턴 조회
2. 공식 문서 표준 확인
3. 업계 베스트 프랙티스 적용
4. 일관성 검증 및 개선

## 9. 경계 및 제한사항

### 9.1 Will (수행 사항)

**수행**:
- 지능적 조직화 및 크로스 레퍼런싱을 포함한 포괄적 프로젝트 문서 생성
- 체계적 분석 및 품질 검증을 위한 멀티 페르소나 조정
- 프레임워크별 패턴 및 확립된 문서 표준 제공

### 9.2 Will Not (미수행 사항)

**미수행**:
- 명시적 업데이트 권한 없이 기존 수동 문서 덮어쓰기
- 적절한 프로젝트 구조 분석 및 검증 없이 문서 생성
- 확립된 문서 표준 또는 품질 요구사항 우회

### 9.3 제한사항

1. **의존성**: MCP 서버 (Sequential, Context7) 설치 필요
2. **복잡도**: 대규모 프로젝트는 처리 시간 증가
3. **맞춤화**: 자동 생성 문서는 수동 편집 필요할 수 있음
4. **업데이트**: 코드 변경 시 문서 수동 업데이트 필요

## 10. 활용 시나리오

### 10.1 신규 프로젝트 문서화

```
/sc:index . --type docs
```

**결과**:
- 전체 프로젝트 문서화
- 설치 가이드
- 사용 가이드
- 아키텍처 문서

### 10.2 API 문서 생성

```
/sc:index src/api --type api --format json
```

**결과**:
- API 엔드포인트 문서
- JSON 형식 출력
- 예제 코드 포함
- 에러 처리 문서

### 10.3 프로젝트 구조 문서

```
/sc:index . --type structure
```

**결과**:
- 디렉토리 구조 트리
- 모듈 설명
- 의존성 그래프
- 컴포넌트 관계

### 10.4 README 생성

```
/sc:index . --type readme
```

**결과**:
- 프로젝트 소개
- 빠른 시작 가이드
- 주요 기능 설명
- 설치 및 사용 방법

## 결론

`/sc:index` 명령은 다음과 같은 방식으로 동작합니다:

1. **MCP 통합**: Sequential과 Context7을 활용한 체계적 분석 및 패턴 적용
2. **멀티 페르소나**: Architect, Scribe, Quality의 협업을 통한 전문적 문서화
3. **5단계 프로세스**: 분석 → 조직화 → 생성 → 검증 → 유지보수
4. **다양한 문서 타입**: API, 구조, 일반 문서, README 지원
5. **지능적 조직화**: 크로스 레퍼런싱 및 탐색 최적화

이 메커니즘을 통해 프로젝트의 포괄적이고 전문적인 문서화가 가능합니다.

