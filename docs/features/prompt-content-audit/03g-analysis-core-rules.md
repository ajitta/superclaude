# 03g — core/rules 심층 감사 (2차)

**대상:** `src/superclaude/core/rules/RULES_{QUALITY,INTERACTION,DELEGATION,DOCS}.md`

**전달 방식:**
- `context_loader.py`의 TRIGGER_MAP이 사용자 입력에 맞춰 이 파일들을 on-demand로 주입한다.
- 서브에이전트에게는 전달되지 않는다.
- 사용자 프로젝트로 배포된다.

**참고:**
- 줄 번호는 감사 시점 기준이다(커밋 `1a55b199`, 2차 감사 직전).
- 1차 감사(03a)에서 이미 보고된 항목은 제외했다.
- 감사자 2명이 각각 격리된 컨텍스트에서 수행했고, 격리 위반은 없었다.
- 수정은 커밋 `9a247cb6`에 들어갔다.

## 요약

- 근거가 붙은 규칙이 많아 전반적인 품질은 높다. delegate_packet, Expiry test, R12의 가역성 분기가 그 예다.
- 위험은 다음 세 곳에 몰려 있었다.
  1. 프레임워크 유지보수자용 지시가 사용자 프로젝트로 샌다(:95 설치본 수정 제안).
  2. 규칙과 예시가 반대다(R20 ↔ "adds tests").
  3. 실행 조건이 정의되지 않았다. 물을 수 없는 환경, 볼 수 없는 바이트 수, 없을 수 있는 Workflow 도구가 여기에 해당한다.
- RULES_INTERACTION은 모든 `/sc:` 호출에 주입되는데, 언제 써야 하는지 조건이 없었다. 그래서 메뉴를 남발하고, 명령이 정한 고유 라벨과 충돌했다.

## RULES_QUALITY / RULES_INTERACTION

| 심각도 | 위치 | 근거 | 문제 | 처리 |
|---|---|---|---|---|
| High | QUALITY:95 | "propose addition to the matching `core/rules/` module" | 사용자 프로젝트에서는 재설치 때 덮어써지는 설치본 `.claude/superclaude/`를 고치라는 제안이 된다. 커널 :29의 gotchas 경로와도 충돌한다 | **적용**: `.claude/rules/gotchas/<domain>.md`로 보내고, superclaude 소스 저장소일 때만 src 수정을 제안 |
| Med-High | INTERACTION:7-12 | `note="… — all commands"`, when 조건 없음 | `/sc:\w+`가 들어간 모든 프롬프트에 주입되어, 매 응답 끝에 메뉴를 붙이게 된다. R12의 bounded-proceed와 반대다 | **적용**: 사용자 선택을 기다리는 단계에서만 메뉴를 쓰도록 when 조건을 추가 |
| Med-High | INTERACTION:8 ↔ brainstorm·init | "[N] flat" ↔ `[a]/[b]/[c]` | 두 규칙이 동시에 주입되면 라벨 체계가 충돌한다 | **적용**: 명령이 정한 라벨을 우선 |
| Med | INTERACTION ↔ intent | AskUserQuestion과 텍스트 메뉴 사이의 우선순위가 없음 | 어느 쪽으로 물을지 모호하다 | **적용**: 명령이 도구를 지정하면 도구를 사용 |
| Med | QUALITY:20 ↔ :25 | "failing repro test passes" ↔ Wrong "adds tests" | 버그 수정에서 반대 신호가 두 개 나온다. canary `bugfix-scope-creep`은 변경 파일 수를 2개 이하로 제한한다 | **적용**: 기존 실패 테스트나 일회성 명령으로 재현. 예시는 "unrequested test files"로 수정 |
| Med | QUALITY:21 | "ONE bounded recovery probe" ↔ "Cap: 2 recovery attempts" | 재시도가 1회인지 2회인지 모호하다 | **적용**: 다른 방법으로 1회 시도하고, 같은 실패로 2회 실패하면 멈춘 뒤 보고 |
| Med | QUALITY:21 | "askuserquestion-rejection-fallback" | 저장소 로컬 gotcha 이름이라 배포본에서는 해석되지 않는다 | **적용**: 해당 행동(재질문하지 않음, 가정을 밝히고, 가역적인 최소 단계를 실행한 뒤 diff 제시)을 본문에 직접 씀 |
| Med | QUALITY:90 | "keywords or paths match: `auth`…" | 부분 문자열로 매칭하면 `author`도 Level 4가 된다. 문서 변경인데도 L4로 올라갈 수 있다 | **적용**: 코드가 실제로 하는 일로 판단하고, 문서는 L0 유지 |
| Med | QUALITY:10 | "check environment (ports, processes, branches) before reading code" | 순수 로직 버그에도 `ps`나 포트 확인을 먼저 하게 된다 | **적용**: 증상이 런타임에서 비롯될 수 있을 때로 한정 |
| Med | QUALITY:44-45 | "reject if ≤3 lines used", "no release in a year" | 측정할 수 없다. 유지보수 사실을 지어낼 위험이 있고, 사용자가 지정한 라이브러리까지 거부할 수 있다 | **적용**: Claude가 직접 고를 때만 적용하고, 확인하지 않은 사실은 unverified로 표시 |
| Med | QUALITY:52 | "refuses logic simplification" | 명시적인 요청을 거부하는 본보기가 된다 | **적용**: ceremony만 단순화하고, 남긴 가드와 그 이유를 보고 |
| Med | QUALITY:72-79 | Small/Medium/Large 구간 사이에 빈틈 | 1파일 200줄 같은 변경은 어느 구간에도 속하지 않는다 | **적용**: Medium을 "between Small and Large"로 정의 |
| Low | QUALITY:43 | "Exception: design doc explicit scope adjacent improvements → in-scope" | 전보체 | **적용**: 완전한 문장으로 |
| Low | QUALITY:12 | "four trigger classes" (1차 보고) | 나열된 항목 수와 맞지 않는다 | **적용**: "the cases just listed" |
| Low | QUALITY:32 | Intent 예시가 "Correct?"로 끝남 (1차 보고) | 규칙은 state-and-proceed다 | **적용**: auth는 보안 영역이라 ask-first 분기라는 점을 예시에 표시 |
| Low | QUALITY:4, :64, :69, :19 | 유지보수자 메모 | deletion test를 통과하지 못한다 | 보류 |
| Low | QUALITY:12-13, :66, PRINCIPLES:11 | 2개 이상 해석일 때의 처리가 네 곳에 중복 | 토큰을 낭비하고 표현이 서로 어긋날 위험이 있다 | 보류(P2) |

## RULES_DELEGATION / RULES_DOCS

| 심각도 | 위치 | 근거 | 문제 | 처리 |
|---|---|---|---|---|
| High | DOCS:26 | "On 2nd related doc: promote via /sc:promote-feature." | 명령형이라 git mv를 자동으로 실행하라는 뜻으로 읽힌다. promote-feature의 "On request only"와 충돌한다 | **적용**: 제안만 하고, 사용자가 실행할 때만 이동 |
| High | DOCS:29 | slug resolution | 무엇을 무엇과 비교하는지, 물을 수 없는 환경에서 어떻게 하는지가 정의되지 않았다(eval:148이 두 경로를 모두 정답으로 인정하는 원인) | **적용**: 비교 대상과 정확 일치·부분 일치·불일치별 처리를 정의하고, headless 환경에서는 기본값을 쓰고 경로를 명시 |
| Med | DOCS:24-25 | "workflow→plans/", "workflow→-workflow" | `/sc:workflow`는 `/sc:roadmap`으로 이름이 바뀌었다(13548763) | **적용**: roadmap으로 교체(suffix `-workflow`는 roadmap.md와 맞게 유지) |
| Med | DOCS:11 | "Between 25,000 and 30,000 bytes" | 작성 중인 모델은 바이트 수를 볼 수 없다 | **적용**: 작성 후 `wc -c`로 측정하고, 비ASCII 문자는 3바이트임을 명시 |
| Med | DOCS:45 | "Guard with an absence/total lint that checks EVERY occurrence" | 사용자 프로젝트에 lint 인프라를 새로 만들라는 압력이 된다 | **적용**: 이미 있는 검사에만 적용하고, 새 lint는 요청 없이 만들지 않음 |
| Med | DOCS:72, :77 | "file committed", "Plan document committed" | 요청 없는 커밋 지시로 읽힌다 | **적용**: 커밋은 선행 조건이며, 충족되지 않았으면 알리거나 커밋을 제안 |
| Med | DOCS:30 | phase enum ↔ status enum 매핑 없음 | 모델이 phase를 임의로 고른다 | **보류**: 작성자가 매핑을 정해야 함 |
| Med | DOCS:37-45 | Durability routing | CLAUDE.md를 편집할 때 이 모듈이 주입되지 않는다(트리거 정규식) | **보류**: 코드(TRIGGER_MAP) 변경이 필요 |
| Med | DELEGATION:8, :50-56 | "the Workflow tool executes it", `agent()`·`parallel()` | 도구가 있다고 무조건 전제한다 | **적용**: "When the harness exposes the Workflow tool" 조건과 블록 note를 추가 |
| Med | DELEGATION:14 | "the Agent tool returns immediately and notifies on completion" | 하네스 동작을 단정한다(foreground 실행이면 사실이 아님) | **적용**: background delegate일 때로 한정 |
| Low | DELEGATION:9-11, 15 | ">20K tokens", "under 30s", "within 5 minutes" | 측정할 수 없다 | 보류(P2) |
| Low | DELEGATION:56 | ">3-unit change" | 정의가 RULES_QUALITY에만 있다 | **적용**: ">3 files/modules/services"로 풀어 씀 |
| Low | DELEGATION:8, 55, 61 | "SC decides", "SC governance", "SC-norm" | 모듈이 단독으로 주입되면 정의되지 않은 약어다 | **적용**: 일반 표현으로 |
| Low | DOCS:59 | "Stable because slugs locked" | archive로 옮기면 링크가 깨진다 | **적용**: "until the folder is archived" |
| (1차) | DOCS:27, :67, :74; DELEGATION:15, :25 | cutoff 날짜, 사용자명 `ajitta`, "caught 3 critical reversals", "own harness" | 저장소 이력이 사용자 프로젝트로 샌다 | **적용**: 일반화 |

## 강점

- R12/R13의 가역성 분기는 묻는 예시와 묻지 않는 예시를 함께 보여 준다.
- R17은 조건부이고 대체 경로까지 있다.
- delegate_packet/delegate_return은 이유를 먼저 제시하고, 예외 처리 순서를 명시한다.
- Expiry test는 사건 기반이라 모델이 실제로 적용할 수 있다.
- :91 skip protocol과 :97 "~ 추정치" 규칙은 수치를 지어내지 못하게 막는다.
