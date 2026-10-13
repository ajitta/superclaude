---
status: draft
revised: 2026-10-13
---

# `sc-author` 설계 — C4 검사기

[04-design.md](./04-design.md)의 C4를 크기 때문에 나눈 문서. 결정(D1–D17)과 다른 컴포넌트는 본 문서에 있다. N1–N4가 쓰이는 흐름: [04b-design-common-pass.md](./04b-design-common-pass.md).

## 인터페이스

```
superclaude author-check <path> [--type skill|agent|command|output-style|memory|generic]
                                [--format md|xml] [--with <path> ...]
```

- `--type` 생략 → 경로로 추론: `*/skills/*/SKILL.md` → skill, `*/agents/*.md` → agent, `*/commands/**.md` → command, `*/output-styles/*.md` → output-style, `CLAUDE.md`·`CLAUDE.local.md`·`AGENTS.md`·`*/rules/**.md` → memory → 그 밖의 md는 generic (D14: 공통 규칙 R·S2·X·N만)
- `--format` 생략 → frontmatter, 빈 줄, HTML 주석(`<!-- -->`), `@path` import 줄을 건너뛴 첫 줄이 태그면 xml, 아니면 md
- 태그 인식: `</?[a-z][a-z0-9_]*(\s[^>]*)?/?>` 패턴만 태그. `<3`, `<5KB`, `<=` 같은 산문 표기는 텍스트. 코드 펜스·인라인 코드는 가린 뒤 검사
- `--with`: load-set(D15)의 다른 문서. N3·N4만 이 범위를 봄, 다른 규칙은 `<path>`에만
- frontmatter 파싱: `yaml.safe_load` (남의 저장소 문서를 검사할 수 있음)
- 링크 해석: `${CLAUDE_SKILL_DIR}`를 검사 대상 스킬 디렉터리로 치환한 뒤 존재 확인
- 출력: 한 줄에 하나 `path:line: CODE message`, 마지막 줄 요약 `N errors, M warnings`
- exit: 0 = error 없음 · 1 = error 있음 · 2 = 사용법 오류·`--with` 경로 없음
- 의존성: 표준 라이브러리 + PyYAML(이미 의존성)
- 위치: `src/superclaude/cli/author_check.py` + `main.py`에 click 명령 등록 (기존 `verify-drift`와 같은 평면 이름)

## 규칙

| 코드 | 등급 | 조건 |
|---|---|---|
| F1 | error | frontmatter 없음(필요한 유형) 또는 YAML 파싱 실패 — Claude Code는 이 경우 필드 없이 조용히 로드 |
| F2 | error | `required` 필드 누락 |
| F3 | error | 그 유형의 `unsupported` 필드 사용 (예: command의 `name`·`paths`) — 조용히 무시됨 |
| F4 | warning | `fields.yaml`에 없는 필드 — Claude Code가 새 필드를 추가했을 수 있으므로 error 아님 |
| F5 | error | 이름 규칙 위반 (skill: 소문자·숫자·하이픈, ≤64 / agent: `:` 금지) |
| F6 | error | skill `description` + `when_to_use` > 1,536자 (목록에서 잘림) |
| F7 | warning | description 1인칭·2인칭 ("I can", "You can") |
| R1 | error | SKILL.md가 링크한 참고 파일 없음 |
| R2 | warning | 참고 파일이 다른 참고 파일을 링크 (깊이 >1) |
| R3 | warning | 100줄 넘는 참고 파일에 목차 없음 |
| S1 | warning | 길이 초과: SKILL.md >500줄, CLAUDE.md·rules >200줄 |
| S2 | warning | 대문자 강조어(MUST, ALWAYS, NEVER, CRITICAL, IMPORTANT) 3회 이상 |
| X1 | error | (xml) 루트 요소가 정확히 하나가 아님, 또는 루트 밖에 맨 텍스트. memory는 루트 앞의 `@path` 줄·HTML 주석 허용 |
| X2 | error | (xml) 태그 짝 불일치·잘못된 중첩 |
| X3–X6 | — | 삭제 (D18, [05-plan.md](./05-plan.md) "구현 시작 결정"): snake_case·깊이·헤더·슬롯 이름은 이 저장소 관례. 태그 이름·깊이·섹션은 대상 프로젝트의 기존 문서를 따름 |
| X7 | error | `--format xml`인데 output-style 유형 (D8 범위 밖) |
| N1 | error · warning | 가리키는 곳 없음. error: Markdown 링크 대상, `path#anchor`의 앵커(대상 헤딩), memory `@path` import 줄 (R1이 잡는 SKILL.md 링크는 제외). warning: 인라인 코드 속 경로(`/`와 확장자 포함, `<`·`*`·`{`·`$` 자리표시자 없음)가 저장소 루트(`git rev-parse --show-toplevel`, 없으면 현재 디렉터리) 기준으로 없음 — 예시 경로일 수 있음 |
| N2 | error | agent에 `tools`가 있는데 본문 인라인 코드 속 도구 이름(`fields.yaml` `tool_names`)·`mcp__<server>__<tool>`이 `tools`에 없음 — 쓰라는 지시면 실행 불가, 쓰지 말라는 지시면 no-op. `tools`가 없으면(전부 상속) 검사 안 함 |
| N3 | error | 같은 항목이 반대 칸에: 칸 = 허용(Always·Do·Proceed·`<does>`) · 확인(Ask First) · 금지(Never·Don't·`<never>`), XML 요소, 헤딩·굵은 라벨 아래 목록 항목, `- Never: a, b` 같은 라벨 줄의 쉼표 구분 항목. 정규화(소문자, Markdown·문장부호 제거, 공백 하나) 후 같은 항목이 두 칸에 → load-set 전체에서 |
| N4 | warning | load-set 안에서 정규화 후 같은 문장 (코드 펜스·frontmatter 제외, 5단어 미만 제외) |

- N 규칙은 같은 입력에 늘 같은 답이 나오는 것만. 뜻이 같은 다른 문장은 `quality.md` 판단 항목 (04b §4)
