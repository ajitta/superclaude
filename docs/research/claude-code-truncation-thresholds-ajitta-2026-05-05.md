---
status: complete
revised: 2026-05-05
---

# Claude Code 문서 Truncation/Omission 임계값 조사

> **요약**: 사용자 커뮤니티에서 떠도는 "한 문서에 1200 토큰 이상이면 생략된다"는 설은 검증 결과 **사실이 아님**. 1200이라는 숫자는 어떤 공식 문서·릴리즈 노트·재현 실험에도 임계값으로 등장하지 않는다. 다만 진짜 임계값 여러 개가 존재하며, 이 문서는 그것들을 검증된 출처와 함께 정리한다.

## 조사 배경

- **질문**: "한 문서에 1200 토큰 이상이 있으면 생략된다는 설이 있는데 진위가?"
- **방법**: Tavily 웹검색 + GitHub 이슈 추적 + Anthropic best-practices 문서 교차 확인
- **조사일**: 2026-05-05

## "1200 토큰" 미신 debunk

`1200`이라는 숫자가 나오는 두 곳 — 둘 다 임계값이 **아니라** 단순 예시 수치:

1. **A B Vijay Kumar Medium**: "Our SKILL.md body is 186 lines, **~1,350 tokens** — well within limits" — 본인 skill 크기 자랑일 뿐
2. **dev.to AI Coding Tip 013**: "SKILL.md (800) + declaration.md (**1,200**) = 2,000 tokens" — progressive disclosure 가상 시나리오 예시

→ 두 글 모두 "1200 토큰 넘으면 잘린다"고 말하지 **않는다**. 누군가 이 예시 숫자를 잘못 기억해 임계값처럼 전달한 것으로 추정.

## 실제 임계값 (검증됨)

| # | 대상 | 임계값 | 종류 | 출처 |
|---|---|---|---|---|
| 1 | Skill `description:` (frontmatter) | **1024자** spec hard limit | 거부됨 | [Issue #44780](https://github.com/anthropics/claude-code/issues/44780), [Issue #230](https://github.com/garrytan/gstack/issues/230) |
| 2 | Skill description `/skills` 목록 표시 | **250자** | 표시만 잘림 | Claude Code 2.1.86 릴리즈 — [Issue #412](https://github.com/backnotprop/plannotator/issues/412) |
| 3 | `<available_skills>` 블록 전체 | **~15K자** 통합 예산 | 일부 skill 목록 숨김 | [Issue #13044](https://github.com/anthropics/claude-code/issues/13044) (92개 → 36개만 표시), [Reddit](https://www.reddit.com/r/ClaudeAI/comments/1psgr91/) |
| 4 | SKILL.md 본문 | **권장 ≤500줄 / ≤5,000 토큰** | **강제 잘림 X** — 가이드라인 | [Anthropic best-practices (obra/superpowers mirror)](https://github.com/obra/superpowers/blob/main/skills/writing-skills/anthropic-best-practices.md) |
| 5 | `MEMORY.md` 인덱스 | **200줄 후** | 하드 컷 | 시스템 프롬프트 명시 ("lines after 200 will be truncated") |
| 6 | Bash tool 출력 | **30,000자 후** | 하드 컷 | 도구 스펙 |
| 7 | Read tool (no `limit` 인자) | **>30KB** | 훅 차단 | SuperClaude R16: <5KB auto-exempt, config(.json/.yaml/.toml/.cfg/.ini/.env) <30KB exempt |
| 8 | Cowork 데스크톱 업로드 (구버그) | **~99KB (98,902 bytes)** | 사일런트 잘림 | [Issue #51435](https://github.com/anthropics/claude-code/issues/51435), 2026-04-21 수정됨 |

## Progressive Disclosure 진짜 동작 원리

문서가 길다고 자동 "생략"되는 게 아니라 **분할 로드**:

1. **세션 시작**: skill frontmatter (~100토큰/skill)만 시스템 프롬프트에 상시 로드
2. **트리거 시**: SKILL.md 본문 전체 로드 (길이 무관, 잘림 X)
3. **참조 시**: 부속 reference 파일 추가 로드

본문 길이 자체는 발화율(activation rate)에 영향을 **거의 주지 않음** — Scott Spence 200+ 테스트 결과: **description 품질**이 발화율의 80-84% vs 50%(나쁜 description) 차이를 결정 ([scottspence.com](https://scottspence.com/posts/how-to-make-claude-code-skills-activate-reliably)).

## 흔한 혼동 (사용자가 들었을 가능성 있는 진짜 사실)

1. **"`/skills`에서 일부가 안 보여요"** → `<available_skills>` 블록 ~15K 예산 초과로 일부 숨김 (Issue #13044). 실제로 **로드는 되어 있고** 발화 가능. 표시만 안 되는 것.
2. **"description이 잘려 보여요"** → 250자 캡 (2.1.86+). description 자체가 250자로 표시 잘림.
3. **"Skill 본문이 너무 길면 안 좋다"** → Anthropic 공식 권장 ≤5,000 토큰. 잘림은 아니지만 cold-start 누적 비용 우려 → 분할 권장.
4. **"긴 CLAUDE.md가 토큰을 먹어요"** → CLAUDE.md는 **항상 전부** 로드됨. 1,200줄 = ~42K 토큰 통째 (Cem Karaca Medium 사례). 잘림은 없지만 매 턴 전체 비용 발생.

## 권장 운영 가이드

| 시나리오 | 권장 |
|---|---|
| Skill 본문 작성 | ≤500줄 목표, 넘으면 reference 파일로 progressive disclosure |
| Skill description | 1024자 이내, 250자 안에 핵심 트리거 포함 |
| 다수 skill 설치 | `<available_skills>` ~15K 예산 인지 — 너무 많으면 목록에서 숨김 발생 |
| MEMORY.md 인덱스 | 200줄 안 유지 — 항목별 한 줄, 본문은 별도 파일 |
| CLAUDE.md | 200~300줄 목표, 도메인 상세는 `.claude/rules/` 또는 skill로 |
| 큰 파일 Read | `limit` 인자 사용, 또는 Grep으로 부분 추출 |

## 결론

**"1200 토큰 임계값은 존재하지 않는다."** 사용자 커뮤니티의 도시전설. 실제로는 위 8가지 별도 임계값이 각각의 메커니즘으로 동작하며, 그중 어느 것도 "한 문서당 1200 토큰" 규칙과 일치하지 않는다.

## 출처

- [Issue #13044 — Skill list truncation threshold](https://github.com/anthropics/claude-code/issues/13044)
- [Issue #412 — 250-char description cap (2.1.86)](https://github.com/backnotprop/plannotator/issues/412)
- [Issue #44780 — 1024-char spec limit](https://github.com/anthropics/claude-code/issues/44780)
- [Issue #51435 — Cowork upload truncation bug](https://github.com/anthropics/claude-code/issues/51435)
- [Anthropic skill best practices](https://github.com/obra/superpowers/blob/main/skills/writing-skills/anthropic-best-practices.md)
- [Reddit — ~15K description budget](https://www.reddit.com/r/ClaudeAI/comments/1psgr91/claude_code_drops_skills_after_a_15k_description/)
- [Scott Spence — Skill activation reliability tests](https://scottspence.com/posts/how-to-make-claude-code-skills-activate-reliably)
- [Cem Karaca — CLAUDE.md 42K token problem](https://medium.com/@cem.karaca/my-claude-md-was-eating-42-000-tokens-per-conversation-heres-how-i-fixed-it-85ffba809bd4)
- [Dotzlaw — Progressive disclosure tier model](https://dotzlaw.com/insights/claude-skills/)
- [bdtechtalks — Claude Skills overview](https://bdtechtalks.substack.com/p/what-to-know-about-claude-skills)
