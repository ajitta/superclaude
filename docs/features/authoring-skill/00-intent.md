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

다른 도구로 만든 문서도 대상이다: "해당 스킬 혹은 도구를 이용하여 만들어도 재 형식화및 검증을 거치려는 의도이다."

## Affected users and systems
- SuperClaude를 설치(`superclaude install`)한 사용자 프로젝트에서 자기 컴포넌트를 만드는 사용자
- SuperClaude 배포판: 이 스킬이 설치본에 들어간다

범위 밖: SuperClaude 자체 콘텐츠 작성(저장소 `.claude/rules/`가 맡음), mode·MCP 문서, hook 작성, claude.ai·Codex 이식.

## Constraints
- "스킬을 명시적으로 발동시킨다. 자동 발동이 아니다."
  - 이유: "skill-creater 류의 meta skill이 이미 많다. 최대한 호환되거나, 충돌되지 않고"
  - 그래서 `/sc-author` 없이 평범하게 요청하면("에이전트 만들어줘") 증상이 그대로 남는다. 받아들인 한계 (04-design.md §8)
- SuperClaude와 결합한다: "superclaude와 결합이 용이한 sc-author를 만드는 것이다."
  - `lean-author`(독립 플러그인, `github.com/ajitta/lean-author`)와 나누는 이유: "lean-author는 superclaude에 종속적이지 않다. 처리할 수 있는 하네스도 없다. 스킬, 에이전트를 만드는 가이드를 제대로 지키는지 확인 불가."
- references는 저장소 rules와 "비슷하지만 다르게 만들어야" 한다: 사용자 프로젝트를 독자로 따로 쓰고, 저장소 rules를 import하지 않는다
- `--xml` 범위: skill·agent·command·memory. output style은 md만

## Open questions
없음. 2026-10-13에 두 질문(lean-author와의 분담, 명시 호출만으로 충분한지)에 답을 받아 Proposed outcome과 Constraints에 옮겼다.
