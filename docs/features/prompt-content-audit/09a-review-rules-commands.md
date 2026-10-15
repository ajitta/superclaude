# 09a — 2차 수정 독립 리뷰

리뷰어 2명이 커밋을 나눠 검토했다. 수정 근거는 주지 않고, 감사 결과를 수용 기준으로만 전달했다.

- **리뷰어 A — 배포 콘텐츠**
  - 대상 커밋: `9a247cb6`, `3a1f6285`, `17204cb6`
- **리뷰어 B — 저장소 로컬 규칙**
  - 대상 커밋: `72445b09`(의미 수정), `3d1475ce`(문법 복원)

반영은 `f2da52b1`(배포)과 `ce239738`(로컬)에서 했다. 리뷰어가 근거로 든 줄 위치와 코드는 오케스트레이터가 원문에서 다시 확인했다.

## 리뷰어 A: 배포 콘텐츠

**판정**
- 감사 항목 거의 전부가 해결됐다. 부분 해결은 1건(R21 복구 횟수)이다.
- 바꾼 description은 모두 300자 이하이고, tier 문장과 Not-for를 갖췄다(최대 272자).

| 심각도 | 지적 | 반영 |
|---|---|---|
| 부분 | R21에 "try one recovery"와 "After 2 failed recoveries"가 같이 남아 있다 | "try up to 2 recoveries, each with a different approach … After the second fails, stop" |
| Med (새 문제) | plan.md:13의 draft 확인이 draft discovery spec에도 "plan anyway"를 허용해, brainstorm의 하드 게이트를 다시 연다. 04-design은 항상 draft라서 design→plan마다 질문이 뜬다 | discovery spec이 draft이면 멈추고 `/sc:review --scope spec`을 안내한다. design 문서는 미해결 Areas of concern이 있을 때만 묻는다 |
| Med (새 문제) | 출력 스타일의 "otherwise use no emoji"가 R21의 `⚠ failed:` 기록과 `--introspect`의 🎯⚡📊💡를 막는다. 이 마커는 FLAGS에만 있고 eval `probe-introspect-marker`가 확인한다 | 예외 목록에 flag와 loaded rule을 추가했다. 단어 수는 600/600을 유지했다 |
| Low (새 문제) | RULES_QUALITY의 "(auth = security → ask-first)" 표시가 auth를 언급하기만 해도 질문을 유도한다 | "(moves files across src/auth/: >3 files in a security area → ask-first)" |
| Low (새 문제) | review의 Spec gate가 리터럴 `--scope spec`에만 걸린다 | Scope 단계가 고른 discovery spec 경로도 포함 |
| Med (누락) | RULES_DOCS:61 Formatter의 "validate + transform + migrate"가 새 cleanup(보고만 하고 `--apply`로만 수정)과 어긋난다 | 바꿨다 |
| Med (누락) | 사용자명이 남아 있다: promote-feature.md:51, verifier.md:65 | `jdoe` |
| Low (누락) | troubleshoot의 "check environment before code"가 무조건 적용된다(R03 과적용 패턴) | 런타임 원인일 수 있을 때로 한정 |
| Low (누락) | roadmap.md:63의 "SC content command", RULES_DOCS:35의 "dist/" | 바꿨다 |
| Low (누락) | cleanup R1이 R3에만 의존하는 무의미한 검사가 됐고, 이름이 R-ID와 헷갈린다 | 보류(P2) |

## 리뷰어 B: 저장소 로컬 규칙

### 72445b09

**판정**
- 대부분 해결됐다.
- 리뷰어가 사실을 확인했다:
  - 2718f713, 672055ce의 내용
  - `_get_injection_tier`(context_loader.py:706-722)의 tier 동작
  - fields.yaml에 `omitClaudeMd` 필드가 있음

| 심각도 | 지적 | 반영 |
|---|---|---|
| 부분 | mcp-authoring의 Anti-Patterns 행에 TIER_0_MAP이 없다. TRIGGER_MAP 예시에 `--c7`(TRIGGER_MAP에 없음)이 있다 | 둘 다 고쳤다 |
| 부분 | `omitClaudeMd`를 "Claude Code settings"라고 불렀는데, 실제로는 agent frontmatter 필드다 | 바꿨다 |
| 부분 | S390을 지운 뒤 남은 "Claude conflated the two"가 근거 없는 순환 인용이 됐다 | 기록되지 않은 세션 관찰에 근거한 저장소 관례라고 명시했다. agent/command 쪽은 포인터만 남겼다 |
| 부분 | Re-sync 문장에 실제 동기화 명령이 없다 | "when it reports an install, run `superclaude install --force --scope <s>`" |
| 부분 | xml-prose-format의 "`thumbs down` button, `tool_search`"(Claude.ai 잔재)가 남아 있다 | 이 저장소의 도구 이름 예시로 바꿨다 |
| Low | command-authoring의 "current limits: fields.yaml"이 가리키는 곳에 공유 예산이 없다(항목별 `listing_chars`만 있음) | "per-entry cap: `listing_chars`"로 바꿨다 |
| Med (새 문제) | gotcha의 "~20%"가 원래는 property-based test 사용률 감소폭인데, over-engineering 감소폭으로 바뀌었다 | 원래 의미로 되돌렸다 |
| Med (새 문제) | compaction-drift는 상시 로드되는 규칙과 중복되지 않는데도 "중복"이라는 이유로 삭제됐다 | 출처 없는 "~50 turns"를 뺀 형태로 복원했다 |
| Low | plan-checklist 삭제 때 "Sub-agents never edit the plan doc"이 사라졌다 | 보류. implement.md는 체크박스를 "main loop"가 표시한다고 쓰므로 그것으로 충분하다고 판단 |
| Low | hook-placeholders-stale이 authoring.md로 옮겨져, docs/ 작업 중에는 로드되지 않는다 | 보류. 대상이 src 문서 작성이라 경로 범위가 맞는다 |
| Low | codex-module-count-drift를 옮기면서 재계산 명령이 빠졌다(320자 예산 때문) | 보류. 테스트 이름으로 찾을 수 있다 |

### 3d1475ce (문법 복원)

**판정**
- 10개 파일에서 약 110문장을 확인했고, 식별자와 코드 스팬은 바뀌지 않았다.
- 의미가 바뀐 곳은 4건이다.

| 위치 | 변화 | 처리 |
|---|---|---|
| agent-authoring:51 | "Two parts" → "Three parts" | 의도한 수정(72445b09의 Negative gate 추가로 항목 수가 셋이 됨) |
| agent-authoring:54 | "name after what" → "name the event it follows" | 의도한 수정(깨진 구문을 해석해서 고침) |
| agent-authoring:106 | "agents that no accept edits" → "should not accept edits" (서술이 규범으로 바뀜) | 되돌림: "do not accept edits" |
| agent-authoring:102 | 금지 규칙이 사실 서술로 바뀜 | 되돌림: "Do not preload skills with …" |

## 검증 (반영 후)

`uv run pytest -q` 결과는 3416 passed, 3 skipped다. 출력 스타일은 600/600단어이고, gotcha 항목은 모두 320자 이하다.
