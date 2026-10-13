---
status: approved-for-plan
revised: 2026-10-13
---

# Intent: SuperClaude 사용자 프로젝트에서 skill·agent·command 문서를 형식에 맞게 만드는 스킬

Author: ajitta.

설계(04-design.md, 2026-10-10) 뒤에 쓴 기록. 원문 요청은 남아 있지 않아 04-design.md §1에 인용된 사용자 말로 다시 구성했다.

## Problem
"superclaude를 설치하여 사용하는 프로젝트에서 추가로 만들 때 너무 형식없이 만들어져"
- 대상 문서: skill, agent, command, output style, memory(CLAUDE.md, CLAUDE.local.md, AGENTS.md, `.claude/rules/*.md`)
- 형식이 어긋나도 드러나지 않음: Claude Code는 잘못된 frontmatter나 지원하지 않는 필드를 오류 없이 무시한다

## Proposed outcome
`/sc-author`로 만들거나 고친 문서가:
1. Claude Code가 실제로 읽는 필드만 쓴다
2. 본문이 한 형식을 따른다: 기본은 Claude Code·Anthropic 공식 권장 구조(`--md`, 사용자 선택), `--xml`이면 SuperClaude식 XML 본문(사용자 요청), 플래그 없이 기존 파일을 고치면 그 파일의 현재 형식
3. XML 규칙을 포함한 기계 검사를 통과한다 (사용자: XML 규칙 검증 필요)

배포 단위는 스킬: "skill이 더 좋지 않아?"

## Affected users and systems
- SuperClaude를 설치(`superclaude install`)한 사용자 프로젝트에서 자기 컴포넌트를 만드는 사용자
- SuperClaude 배포판: 이 스킬이 설치본에 들어간다

범위 밖: SuperClaude 자체 콘텐츠 작성(저장소 `.claude/rules/`가 맡음), mode·MCP 문서, hook 작성, claude.ai·Codex 이식.

## Constraints
- "스킬을 명시적으로 발동시킨다. 자동 발동이 아니다."
  - 그래서 `/sc-author` 없이 평범하게 요청하면("에이전트 만들어줘") 증상이 그대로 남는다. 받아들인 한계 (04-design.md §8)
- references는 저장소 rules와 "비슷하지만 다르게 만들어야" 한다: 사용자 프로젝트를 독자로 따로 쓰고, 저장소 rules를 import하지 않는다
- `--xml` 범위: skill·agent·command·memory. output style은 md만

## Open questions
- `lean-author`와 무엇을 나눠 맡는가. 그쪽 intent(`github.com/ajitta/lean-author` `docs/00-intent.md`, 2026-10-12)도 문제 1번이 같다("agent·skill·command를 만들면 형식 없이 만들어진다"). 다른 점은 SuperClaude 없이도 설치하는 독립 플러그인이라는 것이고, 두 문서 모두 "다른 방향"이라고만 적었다. sc-author만 맡는 몫이 무엇인지, 둘을 합칠지는 정하지 않았다.
- 성공 기준을 무엇으로 볼 것인가. 보고된 증상은 평범한 요청에서 생기는데, 명시 호출만으로 해결하는 것은 `/sc-author`를 불렀을 때의 형식뿐이다. 그 범위면 충분한지는 not stated.
