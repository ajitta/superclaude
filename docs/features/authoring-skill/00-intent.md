---
status: approved-for-plan
revised: 2026-10-13
---

# Intent: SuperClaude 사용자 프로젝트에서 Claude가 읽는 지시·컨텍스트 문서를 형식에 맞게 만드는 스킬

Author: ajitta.

설계(04-design.md, 2026-10-10) 뒤에 쓴 기록. 원문 요청은 남아 있지 않아 04-design.md §1에 인용된 사용자 말로 다시 구성했다.

## Problem
"superclaude를 설치하여 사용하는 프로젝트에서 추가로 만들 때 너무 형식없이 만들어져"
- 대상 문서: skill, agent, command, output style, memory(CLAUDE.md, CLAUDE.local.md, AGENTS.md, `.claude/rules/*.md`)
- 범위 확대 (2026-10-13): "authoring의 범위를 rule파일 claude.md, agent.md, mode, output style , mcp가이드 모든 claude에게 읽혀서 지시, 혹은 컨텍스트 내용으로 들어가는 모든 것을 포함하려고 해"
  - 유형을 정해 늘리는 것이 목적이 아니다: "mode, mcp, hook 에 대해 해당 대상을 명시적으로 규정해서 superclaude에 맞추려는 목적이 아니다. claude에게 읽히는 지시 컨텍스트 문서를 authoring하는 문제이다."
  - 예로 든 것: rule 파일, CLAUDE.md, agent, mode, output style, MCP 가이드, skill 부속 파일, hook 주입 문구, 서브에이전트 프롬프트, auto memory `MEMORY.md`
- 근거로 든 사례: "지금 이 프로젝트의 rules, claude.md, agent.md, 메모리 내용만 봐도 NO-OP의 가능성이 있는 지시가 많아."
- 형식이 어긋나도 드러나지 않음: Claude Code는 잘못된 frontmatter나 지원하지 않는 필드를 오류 없이 무시한다

## Proposed outcome
`/sc-author`로 만들거나 고친 문서가:
1. Claude Code가 실제로 읽는 필드만 쓴다
2. 본문이 한 형식을 따른다: 기본은 Claude Code·Anthropic 공식 권장 구조(`--md`, 사용자 선택), `--xml`이면 SuperClaude식 XML 본문(사용자 요청), 플래그 없이 기존 파일을 고치면 그 파일의 현재 형식 (2026-10-14 D21로 바뀜: 플래그 없는 새 파일은 같은 유형 기존 문서의 형식, 그런 문서가 없을 때만 `--md`)
3. XML 규칙을 포함한 기계 검사를 통과한다 (사용자: XML 규칙 검증 필요)

배포 단위는 스킬: "skill이 더 좋지 않아?"

다른 도구로 만든 문서도 대상이다: "해당 스킬 혹은 도구를 이용하여 만들어도 재 형식화및 검증을 거치려는 의도이다."
- 역할 분담: "skill-creator 종류가 충분히 잘 만들거라고 생각한다. 그것을 재형식화하고 no-op들을 제거하는 과정이라고 생각하는 것이 맞다." sc-author는 내용을 새로 짓기보다 형식을 맞추고 결과를 바꾸지 않는 문장을 걷어낸다

## Affected users and systems
- SuperClaude를 설치(`superclaude install`)한 사용자 프로젝트에서 자기 컴포넌트를 만드는 사용자
- SuperClaude 배포판: 이 스킬이 설치본에 들어간다

범위 밖: SuperClaude 자체 콘텐츠 작성(저장소 `.claude/rules/`가 맡음), claude.ai·Codex 이식.
- SuperClaude 자체 문서 (2026-10-13): "sc 자체 문서는 포함하지 않는다. sc 프로젝트를 위한 내용은 이 프로젝트에만 남아 있어. 이것을 설치해서 사용하는 프로젝트에서 사용자가 command, agent, skill 등을 확장할 수 있게 하려고 하는 것이다." 위 근거 사례(이 저장소의 no-op)는 문제를 보여 주는 예일 뿐 작업 대상이 아니다

## Constraints
- "스킬을 명시적으로 발동시킨다. 자동 발동이 아니다."
  - 이유: "skill-creater 류의 meta skill이 이미 많다." 그런 스킬과 발동이 겹치지 않게 한다 ("호환"은 모호하다는 지적으로 위 역할 분담으로 대체, 2026-10-13)
  - 그래서 `/sc-author` 없이 평범하게 요청하면("에이전트 만들어줘") 증상이 그대로 남는다. 받아들인 한계 (04-design.md §8)
- SuperClaude와 결합한다: "superclaude와 결합이 용이한 sc-author를 만드는 것이다."
  - `lean-author`(독립 플러그인, `github.com/ajitta/lean-author`)와 나누는 이유: "lean-author는 superclaude에 종속적이지 않다. 처리할 수 있는 하네스도 없다. 스킬, 에이전트를 만드는 가이드를 제대로 지키는지 확인 불가."
- references는 저장소 rules와 "비슷하지만 다르게 만들어야" 한다: 사용자 프로젝트를 독자로 따로 쓰고, 저장소 rules를 import하지 않는다
- `--xml` 범위: skill·agent·command·memory. output style은 md만
- 예시: "레퍼런스 문서에 예시를 넣을 필요가 있다면 3-5개 수준" (Anthropic 가이드)
- 최신 가이드 기준: "이 skill제작, prompt가이드는 빠르게 업데이트되고 있어서 항상 claude의 최신 모델 기준이어야한다. fable, opus, sonnet의 최신 버전 기준의 가이드를 이용해야돼. stale된것 들로 만들면 안된다."

## Open questions
- 2026-10-13의 두 질문(lean-author와의 분담, 명시 호출만으로 충분한지)은 답을 받아 Proposed outcome과 Constraints에 옮겼다.
- 사용자 질문 "이 스킬이 완성되면 rules의 authoring 관련 문서는 필요 없어지지 않아?"는 범위 밖 결정("sc 프로젝트를 위한 내용은 이 프로젝트에만 남아 있어")으로 답이 됨: 저장소 rules는 남는다.
