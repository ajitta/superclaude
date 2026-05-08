---
status: complete
revised: 2026-05-09
---

# XML vs Markdown 포맷의 토큰 비용과 권장 강도 변화 — Opus 4.7 시점 재평가

**Author**: ajitta
**Date**: 2026-05-09
**Trigger**: SuperClaude 명령어(`/sc:*`)가 XML 구조를 의무화하고 있는데, Opus 4.7 시점에서 그 비용/효용이 여전히 정당화되는가?
**Method**: (1) 실측 토큰 비교 — 가장 큰 명령어 파일 1건을 XML/Markdown 두 버전으로 토크나이즈, (2) Anthropic 공식 가이드 + 외부 분석 글의 권장 강도 변화 조사

---

## 1. 실험: 실제 Claude 토큰량 비교

### 대상

- `src/superclaude/commands/insight.md` — 34개 명령어 중 가장 큰 파일 (7,170 bytes, 112줄)

### 방법

`claude -p --model sonnet --output-format json` 의 `usage.input_tokens + cache_creation_input_tokens + cache_read_input_tokens` 합계로 측정. baseline 1회 + 두 버전 각각 → delta로 파일 토큰 추출. 워밍업 3회로 캐시 안정화.

```python
# 핵심 측정 로직
def total_input(resp): return u['input_tokens'] + u['cache_creation_input_tokens'] + u['cache_read_input_tokens']
xml_tokens  = total_input(file_xml_resp) - total_input(baseline_resp)
md_tokens   = total_input(file_md_resp)  - total_input(baseline_resp)
```

### 결과

| 측정기 | XML 버전 | Markdown 버전 | 절감 | 절감률 |
|---|---:|---:|---:|---:|
| `tiktoken` (cl100k_base, OpenAI) | 1,766 | 1,632 | 134 | **-7.6%** |
| **Claude (sonnet 4.6, 실측)** | **2,243** | **1,994** | **249** | **-11.1%** |

### 관찰

1. **Claude 토크나이저가 cl100k보다 ~22-27% 더 많이 카운트** — 특히 XML 닫는 태그/속성 문법(`</component>`, `command="..."`)에서 격차가 큼.
2. **XML→Markdown 절감률**: cl100k 추정 7.6% → 실측 **11.1%**. XML 스캐폴딩의 실제 비용은 OpenAI 토크나이저로 추정한 것보다 높음.
3. **변동성 노이즈**: baseline 3회에서 cache_creation ±47 토큰 흔들림 — 249토큰 delta는 노이즈의 5배이므로 결과 신뢰 가능.
4. **34개 명령어 전체로 외삽**: 평균 1,500토큰 × 11% × 34 ≈ **~5,600 토큰** 이론적 절감 (slash 호출 시점 로드 기준).

---

## 2. 조사: Anthropic 공식 권장 강도의 변화

### 2.1 Anthropic 공식 — 명시적 후퇴

[Effective context engineering for AI agents (Anthropic Engineering, 2025)](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents):

> "...using techniques like XML tagging **or Markdown headers** to delineate these sections, **although the exact formatting of prompts is likely becoming less important as models become more capable.**"

**해석**: 이전 가이드의 "Use XML tags" 절대 권장 → XML과 Markdown 헤더를 동등 선택지로 병기, 그리고 "포맷 자체는 점점 덜 중요해진다"고 명시. **권장 강도가 약화된 가장 강한 1차 증거**.

### 2.2 Skill 작성 가이드 — XML **금지**

[The Complete Guide to Building Skills for Claude (Anthropic PDF)](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf):

> "**Forbidden in frontmatter: XML angle brackets (< >)**"
> "No XML tags (< >) anywhere [in description]"

[Skill authoring best practices — Claude API Docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices): SKILL.md 본문 템플릿 모두 `##`/`###` Markdown 헤더 기반. Anthropic 자체 콘텐츠 프레임워크는 XML이 아닌 Markdown으로 통일됨.

### 2.3 Opus 4.7 토큰 효율 가이드 — XML 탈신비화

[Claude 4.7 Token Efficiency Playbook (liatbenzur.com)](https://liatbenzur.com/2026/04/20/claude-4-7-token-efficiency-playbook-cut-costs-reduce-bot-blocking/):

> "Use boundaries like `<task>`, `<context>`, `<constraints>`. **Do this because it reduces ambiguity, not because XML is magic.**"

**해석**: XML의 "마법" 지위 명시적 부정. 본질은 **"경계 표시"**이고 그 수단이 XML이든 Markdown이든 부차적.

### 2.4 다만 복잡 프롬프트엔 여전히 권장

[Claude Opus 4.7 Isn't a Drop-in Replacement (Daily Dose of DS)](https://blog.dailydoseofds.com/p/claude-opus-47-isnt-a-drop-in-replacement):

> "Use XML tags to structure **complex prompts**. Wrap instructions, context, examples, and inputs in their own tags to reduce misinterpretation."
> "Use 3-5 examples wrapped in `<example>` tags."

**해석**: 완전 폐기는 아님. 다중 섹션 + few-shot examples가 있는 복잡 프롬프트엔 여전히 유효한 도구.

### 2.5 4.7 핵심 변화: 문자 그대로 따름 (literal-instruction-following)

[15 Best System Prompts for Claude Opus 4.7 (chatlyai)](https://chatlyai.app/blog/best-system-prompts-for-claude-opus-4-7) + [Claude Opus 4.7 Deep Dive (Caylent)](https://caylent.com/blog/claude-opus-4-7-deep-dive-capabilities-migration-and-the-new-economics-of-long-running-agents):

> "**Opus 4.7 treats suggestions as optional and directives as required.**"
> "Replace 'consider,' 'you might' with 'you must,' 'always,' 'never.'"

**해석**: directive 강도(절대 금지/필수)는 **declarative voice**가 만들고, XML 태그 자체가 아님. Markdown에서도 `**NEVER:**` + 명령형 문장으로 동일 효과 달성 가능.

---

## 3. 종합: SuperClaude의 XML 채택 근거 재평가

| 이전 주장 | 현재 평가 |
|---|---|
| "Anthropic 자체 문서가 *Use XML tags to structure prompts* 권장" | **부정확** — 현 가이드는 "XML or Markdown, 포맷은 덜 중요" |
| "`<does>`/`<never>` 태그가 directive 강도를 만든다" | **부분 참** — 강도는 declarative voice가 만들고, XML은 그 voice를 격리해주는 보조 수단 |
| "Markdown으로 가면 boundary 신호 약해짐" | **부분 참** — 4.7은 더 literal해서 `**NEVER**` 같은 markdown 강조도 거의 동등 처리 |
| "테스트 가능성/스펙 강제력" | **여전히 유효** — XML 파싱은 markdown 헤더보다 결정적, `test_command_structure.py`의 가치는 변함 없음 |
| "동형 컨테이너 분리 (`<examples>` vs `<example>`)" | **여전히 유효** — 같은 이름 헤더로는 표현 불가능 |
| "11% 토큰 손해는 의미 있는 ROI인가" | **약함** — 실측 -11% (5,600토큰 외삽)는 의미 있지만 spec/테스트/문서 전체 갈아엎는 비용에 못 미침 |

### 결정적 약화 포인트

XML의 **모델 처리 우위 논거**는 상당 부분 약화됨. 이 프로젝트가 XML을 유지하는 진짜 강한 이유는 다음 두 가지로 좁혀짐:

1. **테스트 가능성** — `<role command="...">`, `<does>`, `<never>` 같은 구조적 attribute/sub-tag 검증 (`test_command_structure.py`). Markdown 자유 형식으로는 같은 수준의 enforce가 어려움.
2. **동형 컨테이너 분리** — `<examples>` (compact lookup table) vs `<example>` (rich free-form illustration). Markdown은 헤더만으로 두 의도를 구별하기 어려움 (단/복수 헤더 차이는 시각적이지 의미적이지 않음).

### 결정적 변화 포인트

- Anthropic의 **자체 콘텐츠 프레임워크인 Skill**이 XML을 명시적으로 **금지**(frontmatter)하고 본문 가이드도 Markdown 기반으로 통일.
- "포맷이 덜 중요해진다"는 Anthropic의 1차 입장.
- 4.7의 literal-following 개선으로 markdown 라벨도 충분히 strict하게 처리됨.

---

## 4. 권고

### 4a. 기존 콘텐츠 (33 commands + 23 agents)
**유지 권고** — 갈아엎는 비용 vs ~5,600토큰 절감의 ROI가 안 맞음. spec/테스트/문서 일체화 비용이 더 큼.

### 4b. 신규 콘텐츠 (특히 신규 skill)
**Markdown 우선 검토** — Anthropic 공식 Skill 가이드가 XML 금지/Markdown 권장으로 통일된 점을 반영. SuperClaude의 신규 skill 작성 시 `xml-prose-format.md` 적용 여부를 재고.

### 4c. 모니터링 항목
- Anthropic이 후속 가이드에서 Markdown 권장을 더 강화하면 4a 결정도 재평가 필요.
- 토크나이저가 Opus 4.8 이상에서 다시 변하면 11% 절감률도 재측정 필요.

---

## 5. 재현 방법

### 5.1 Markdown 변환 버전 생성

`insight.md`의 XML 태그를 Markdown 헤더로 1:1 매핑:
- `<component name="insight" type="command">` 래퍼 제거
- `<role command="..."><mission>...</mission></role>` → `# /sc:insight` + `## Mission`
- `<flow>`, `<outputs>`, `<storage>`, `<schema>`, `<tools>`, `<script_reference>`, `<examples>`, `<auto_harvest_behavior>`, `<gotchas>` → `## Section Name`
- `<bounds><does>...</does><never>...</never><fallback>...</fallback></bounds>` → `## Bounds` + `- Does:` / `- Never:` / `- Fallback:`
- `<handoff next="..."/>` → `## Handoff` + `Next: ...`
- frontmatter 그대로 유지

### 5.2 측정 스크립트

```python
# _count_via_claude.py (재현용 골격)
import json, subprocess
from pathlib import Path

def run(prompt):
    p = subprocess.run(
        ["claude", "-p", "--model", "sonnet", "--output-format", "json"],
        input=prompt, capture_output=True, text=True, encoding="utf-8", timeout=300,
    )
    return json.loads(p.stdout)

def total(r):
    u = r["usage"]
    return u["input_tokens"] + u["cache_creation_input_tokens"] + u["cache_read_input_tokens"]

SUFFIX = "\n\n---\n\nReply with just: OK"
xml = Path("src/superclaude/commands/insight.md").read_text(encoding="utf-8")
md  = Path("insight_markdown_version.md").read_text(encoding="utf-8")

for _ in range(3): run("Reply with just: OK")  # warm cache
base = total(run("Reply with just: OK"))
print("XML:", total(run(xml + SUFFIX)) - base)
print("MD :", total(run(md + SUFFIX))  - base)
```

**주의사항**:
- 파일 내용을 CLI 인자로 전달하면 frontmatter `---`가 플래그로 파싱됨 → **반드시 stdin으로 전달**.
- 동일 세션 cache_creation 변동(±50토큰)은 정상 — delta가 노이즈보다 충분히 큰지 확인.

---

## 출처 (Sources)

- [Effective context engineering for AI agents — Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [The Complete Guide to Building Skills for Claude (PDF) — Anthropic](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf)
- [Skill authoring best practices — Claude API Docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [Claude Opus 4.7 Isn't a Drop-in Replacement for 4.6 — Daily Dose of DS](https://blog.dailydoseofds.com/p/claude-opus-47-isnt-a-drop-in-replacement)
- [15 Best System Prompts for Claude Opus 4.7 — chatlyai](https://chatlyai.app/blog/best-system-prompts-for-claude-opus-4-7)
- [Claude 4.7 Token Efficiency Playbook — liatbenzur.com](https://liatbenzur.com/2026/04/20/claude-4-7-token-efficiency-playbook-cut-costs-reduce-bot-blocking/)
- [Claude Opus 4.7 Deep Dive — Caylent](https://caylent.com/blog/claude-opus-4-7-deep-dive-capabilities-migration-and-the-new-economics-of-long-running-agents)
- [How to Prompt Claude Opus 4.7 Differently Than 4.6 — MindStudio](https://www.mindstudio.ai/blog/how-to-prompt-claude-opus-4-7)
- [Changes in the system prompt between Claude Opus 4.6 and 4.7 — Simon Willison](https://simonwillison.net/2026/apr/18/opus-system-prompt/)
- [Prompt engineering overview — Claude API Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview)
