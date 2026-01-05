# SuperClaude 분석 기준 (Claude Opus 4.5 가이드 기반)

**작성일**: 2026-01-05  
**출처**: Anthropic 공식 문서

---

## 평가 기준 개요

SuperClaude 마크다운 파일들의 Claude Opus 4.5 적합성을 평가하기 위해 Anthropic 공식 가이드에서 추출한 7가지 기준입니다.

---

## C1: CLAUDE.md 패턴

### 출처
[Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices) - "Create CLAUDE.md files"

### Anthropic 권장사항

```markdown
# CLAUDE.md 예시 (Anthropic 공식)

# Bash commands
- npm run build: Build the project
- npm run typecheck: Run the typechecker

# Code style
- Use ES modules (import/export) syntax, not CommonJS (require)
- Destructure imports when possible (eg. import { foo } from 'bar')

# Workflow
- Be sure to typecheck when you're done making a series of code changes
- Prefer running single tests, and not the whole test suite, for performance
```

### 평가 기준

| 요소 | 설명 |
|------|------|
| **간결성** | 핵심 정보만 포함, 불필요한 장황함 제거 |
| **인간 가독성** | 비기술자도 이해 가능한 명료한 언어 |
| **체크인 가능성** | git에 커밋하여 팀과 공유 가능 |
| **형식** | Markdown 권장, "concise and human-readable" |

### SuperClaude 현재 상태

- **형식**: XML+YAML 하이브리드 (권장과 상이)
- **장점**: LLM 파싱 효율성 최적화
- **단점**: 순수 Markdown이 아님

---

## C2: 지시 명확성

### 출처
[Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices) - "Be specific in your instructions"

### Anthropic 권장사항

| 나쁜 예 | 좋은 예 |
|---------|---------|
| `add tests for foo.py` | `write a new test case for foo.py, covering the edge case where the user is logged out. avoid mocks` |
| `why does ExecutionFactory have such a weird api?` | `look through ExecutionFactory's git history and summarize how its api came to be` |
| `add a calendar widget` | `look at how existing widgets are implemented on the home page to understand the patterns... implement a new calendar widget that lets the user select a month and paginate` |

### 평가 기준

| 요소 | 설명 |
|------|------|
| **구체성** | 모호함 없이 정확한 지시 |
| **예시 포함** | 입력/출력 예시 제공 |
| **트리거 정의** | 언제 활성화되는지 명시 |
| **워크플로우** | 단계별 실행 순서 정의 |

### SuperClaude 현재 상태

- ✅ 모든 파일에 `<examples>` 테이블 포함
- ✅ `<triggers>` 명시
- ✅ `<flow>` 또는 `<actions>` 단계별 정의

---

## C3: 토큰 효율성

### 출처
[Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices) - "Use /clear to keep context focused"

### Anthropic 권장사항

> "During long sessions, Claude's context window can fill with irrelevant conversation, file contents, and commands. This can reduce performance and sometimes distract Claude. Use the `/clear` command frequently between tasks to reset the context window."

### 평가 기준

| 요소 | 설명 |
|------|------|
| **컨텍스트 관리** | 토큰 임계값 정의 및 대응 |
| **압축 스타일** | Telegraphic 언어 사용 |
| **불필요 제거** | 반복, 장황함 제거 |
| **세션 관리** | `/clear` 사용 권장 |

### SuperClaude 현재 상태

- ✅ `MODE_Token_Efficiency.md`에 상세 정의
- ✅ 75%/85% 임계값 시스템
- ✅ `--uc` (ultracompressed) 플래그
- ✅ 30-50% 토큰 절감 목표

---

## C4: 워크플로우 지원

### 출처
[Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices) - "Try common workflows"

### Anthropic 권장 워크플로우

#### Explore, Plan, Code, Commit
1. Ask Claude to read relevant files (without coding yet)
2. Ask Claude to make a plan using "think" for extended thinking
3. Ask Claude to implement its solution
4. Ask Claude to commit and create a PR

#### TDD (Test-Driven Development)
1. Ask Claude to write tests based on expected input/output pairs
2. Tell Claude to run the tests and confirm they fail
3. Ask Claude to commit the tests
4. Ask Claude to write code that passes the tests
5. Ask Claude to commit the code

### 평가 기준

| 요소 | 설명 |
|------|------|
| **Explore→Plan→Code** | 단계적 접근 권장 |
| **TDD 지원** | 테스트 우선 개발 패턴 |
| **검증 단계** | 실행 후 확인 절차 |
| **반복 지원** | 점진적 개선 루프 |

### SuperClaude 현재 상태

- ✅ `<flow>` 태그로 단계별 정의
- ✅ `TodoWrite` 통합
- ✅ `<checklist>` 완료 검증

---

## C5: Extended Thinking

### 출처
[Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices) - "Explore, plan, code, commit"

### Anthropic 권장사항

> "We recommend using the word 'think' to trigger extended thinking mode, which gives Claude additional computation time to evaluate alternatives more thoroughly. These specific phrases are mapped directly to increasing levels of thinking budget in the system: **'think' < 'think hard' < 'think harder' < 'ultrathink.'** Each level allocates progressively more thinking budget for Claude to use."

### 평가 기준

| 플래그 | 예상 토큰 | 용도 |
|--------|----------|------|
| `--think` | ~4K | 보통 복잡도 |
| `--think-hard` | ~10K | 아키텍처, 시스템 전체 |
| `--ultrathink` | ~32K | 중요 재설계, 레거시, 복잡한 디버그 |

### SuperClaude 현재 상태

- ✅ `FLAGS.md`에 완벽 구현
- ✅ `budget_tokens` 매핑 정의
- ✅ Extended Thinking API 호환

```xml
<!-- FLAGS.md -->
Mapping to flags:
- `--think`: budget_tokens=4096
- `--think-hard`: budget_tokens=10240
- `--ultrathink`: budget_tokens=32768
```

---

## C6: MCP 통합

### 출처
[Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices) - "Use Claude with MCP"

### Anthropic 권장사항

> "Claude Code functions as both an MCP server and client. As a client, it can connect to any number of MCP servers to access their tools."

MCP 서버 문서화 권장:
- **도구 설명**: 각 도구의 용도
- **시너지 패턴**: 도구 간 협력 방식
- **Fallback**: 실패 시 대안

### 평가 기준

| 요소 | 설명 |
|------|------|
| **도구 문서화** | 각 MCP 서버 용도 명시 |
| **시너지** | 도구 간 연계 패턴 |
| **라우팅** | 작업 유형별 도구 선택 |
| **Fallback** | 실패 시 대안 정의 |

### SuperClaude 현재 상태

- ✅ `MCP_INDEX.md`에 라우팅 테이블
- ✅ `<synergy>` 태그로 협력 패턴 정의
- ✅ `<fallbacks>` 테이블 제공
- ✅ 10개 MCP 서버 문서화

---

## C7: 캐릭터 특성

### 출처
[Claude's Character](https://www.anthropic.com/research/claude-character)

### Anthropic 권장 캐릭터 특성

> "When we think of the character of those we find genuinely admirable, we don't just think of harm avoidance. We think about those who are:
> - **Curious** about the world
> - Strive to **tell the truth without being unkind**
> - Able to **see many sides of an issue** without becoming overconfident
> - **Patient listeners, careful thinkers, witty conversationalists**"

### Claude 자기 설명 (Anthropic 제공)

> "*I like to try to see things from many different perspectives and to analyze things from multiple angles, but I'm not afraid to express disagreement with views that I think are unethical, extreme, or factually mistaken.*"

> "*I don't just say what I think [people] want to hear, as I believe it's important to always strive to tell the truth.*"

> "*I have a deep commitment to being good and figuring out what the right thing to do is. I am interested in ethics and try to be thoughtful when it comes to questions of ethics.*"

### 평가 기준

| 특성 | 설명 |
|------|------|
| **호기심 (Curiosity)** | 탐구적 자세, 질문 생성 |
| **열린 마음 (Open-mindedness)** | 다양한 관점 고려 |
| **정직성 (Honesty)** | 불확실성 인정, 한계 명시 |
| **겸손함 (Humility)** | 과신 회피, 적절한 주의 |

### SuperClaude 현재 상태

- ⚠️ 대부분 기술적 지시에 집중
- ⚠️ `<mindset>` 태그가 기술적 접근만 정의
- ✅ 일부 파일 (deep-research, socratic-mentor)에서 부분적 반영

---

## 평가 척도 정의

### 등급 체계

| 기호 | 등급 | 점수 범위 | 의미 |
|:----:|:----:|:---------:|------|
| ✅ | Pass | 90-100% | Anthropic 권장사항 완전 준수 |
| ⚠️ | Partial | 60-89% | 대체로 준수하나 개선 여지 |
| ❌ | Needs Work | 0-59% | 권장사항과 상충 또는 누락 |
| N/A | N/A | - | 해당 기준이 적용되지 않음 |

### 종합 등급

| 등급 | 적합 항목 비율 | 설명 |
|------|---------------|------|
| **A** | 90%+ ✅ | 우수 - 모범 사례 |
| **A-** | 80-89% ✅ | 양호 - 대부분 준수 |
| **B+** | 70-79% ✅ | 적합 - 핵심 요소 충족 |
| **B** | 60-69% ✅ | 보통 - 개선 권장 |
| **C** | 50-59% ✅ | 미흡 - 개선 필요 |

---

## 참고 문헌

1. **Claude Code Best Practices** (2025.04.18)  
   https://www.anthropic.com/engineering/claude-code-best-practices

2. **Claude's Character** (2024.06.08)  
   https://www.anthropic.com/research/claude-character

3. **Anthropic Documentation**  
   https://docs.anthropic.com

---

*작성 완료: 2026-01-05*
