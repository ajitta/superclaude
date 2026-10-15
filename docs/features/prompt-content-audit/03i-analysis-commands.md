# 03i — commands·output-style 감사

## 대상과 방법

- **대상**
  - `src/superclaude/commands/*.md` 37개(README 포함)
  - `src/superclaude/output-styles/plain-language.md`(+README)
- **배포 방식**
  - `/sc:<name>` 명령으로 배포된다.
  - description은 모델에게 보이고, 모델이 스스로 호출할 수 있다(`disable-model-invocation`을 쓰지 않는 것이 저장소 정책).
  - 본문은 메인 스레드 프롬프트가 된다.
  - 출력 스타일은 매 턴 Claude Code의 톤 지시를 대체한다.
- **감사자 4명:** workflow 체인, 기타 13개, 세션·메타 13개+README, 출력 스타일+명령 간 일관성
- **감사 시점:** 커밋 `9a247cb6`
- **수정 커밋**
  - `17204cb6`: 명령 파일·출력 스타일 수정
  - `3a1f6285`: loader `--structured` 트리거 수정과 테스트 추가

## 요약

**잘 지켜진 것**
- 기계 점검 결과:
  - `<syntax>` 플래그 미정의 0건
  - handoff 미해결 0건
  - 카탈로그(sc/help/README) 36/36 일치
  - description 36개 모두 tier 문장과 "Not for" 경계를 갖춤
- 전역 플래그와 이름이 같은 로컬 플래그에 "unrelated to the global …"이 표시되어 있다.
- 출력 스타일은 품질이 높다.

**문제가 몰린 곳**
1. **체인 게이트의 주인이 없음:** brainstorm은 `approved-for-plan`과 Iteration Log를 요구하지만, 이를 수행하는 명령이 없었다.
2. **예시가 규칙을 거스름:** build 의존성 설치, pm 한 줄 수정 위임, brainstorm의 review 생략, agent 이름 인자 등. 현행 모델은 예시를 따른다.
3. **낡은 카탈로그:** select-tool이 Serena·Morphllm 시절 결정표를 그대로 갖고 있었다.
4. **저장소 이력 누수:** cleanup이 2026-05-18 cutoff로 사용자 문서를 일괄 경고했고, 예시에 사용자명이 들어 있었다.
5. **측정할 수 없는 수치:** 94%, ≥80%, 85%, ≥90%, 24h, >30min, ctx 60%.
6. **이름 충돌:** `--structured`가 review와 business-panel에서 다른 뜻인데, loader는 bare `--structured`에 BUSINESS_SYMBOLS를 주입했다.

## 발견사항과 처리

| 심각도 | 위치 | 문제 | 처리 |
|---|---|---|---|
| High | brainstorm:18,20,31,78; review:77 | 게이트의 주인이 없다. review는 수정 금지라 상태를 바꿀 수 없고, "Self-review"라는 이름은 자체 리뷰를 유도한다 | **적용**: review에 Spec gate 단계(Iteration Log 추가, 사용자 승인 시 `approved-for-plan`)와 never 예외를 추가. brainstorm은 draft를 유지하고 review를 직접 대신하지 않음 |
| High | brainstorm:71 | "Correct" 예시가 review와 plan을 건너뛰고 implement로 간다 | **적용** |
| High | build:56 | 예시가 의존성을 설치한다(`<never>` 위반). `uv`는 이 저장소의 전제다 | **적용**: 설치 명령을 보고하고 멈춤 |
| High | cleanup:48 | 저장소 마이그레이션 날짜를 cutoff로 써서 모든 standalone 문서에 경고를 낸다 | **적용**: R1-standalone-valid, 날짜 조건 삭제 |
| High | git:24,49-56 | `claude --from-pr`(터미널 시작 옵션)을 세션 안에서 실행하게 한다 | **적용**: `gh pr checkout`과 `gh pr view` 절차로 교체, CLI 옵션은 Bash로 실행하지 말라고 명시 |
| High | select-tool:26-33 | Serena·Morphllm 결정표가 남아 있고, 측정할 수 없는 점수를 쓰며, 배포되는 MCP를 하나도 다루지 않는다 | **적용**: 작업 유형별 표로 재작성(symbol, text, Context7, Tavily, Playwright, DevTools, memory, 미연결 시 처리) |
| High | pm:28,36 | 한 줄 수정에 sub-agent 3개를 쓰는 예시. 약어는 존재하지 않는 agent 이름이다 | **적용**: 직접 수정으로. 실제 agent 이름 사용 |
| High | save:79 | gotcha가 save 본래의 목적(진행 상황과 다음 행동 저장)을 금지한다 | **적용**: 대상을 auto memory로 한정 |
| Med | plan:15 vs 53-58 | phase는 커밋 1회인데, 템플릿은 task마다 커밋한다 | **적용**: phase 단위로 커밋 |
| Med | plan:13 | feature 폴더의 04-design과 01-discovery를 읽지 않고, draft 게이트도 없다 | **적용** |
| Med | implement:14-19 | 커밋된 plan에 다시 승인을 받는다. "plan mode"는 Claude Code의 Plan Mode로 오독될 수 있다 | **적용**: `--plan` 호출 자체를 승인으로 봄 |
| Med | review:71 / :20, 61-66 | scope-focus가 자체 예시와 모순된다. 리뷰를 받는 쪽의 push-back 프로토콜이 들어 있다 | **적용**: diff 범위에서만 변경분을 리뷰. 리뷰어 자기검증(Keep/Withdraw/Downgrade) |
| Med | loader:128 | `/sc:review --structured`에 BUSINESS_SYMBOLS가 주입된다 | **적용**: `/sc:business-panel …--structured`로 한정하고 테스트 추가 |
| Med | roadmap:15-16,38 vs 63 | "Execute"와 "does not run agents"가 같은 파일 안에서 충돌한다 | **적용**: 자문만 받고 실행하지 않음 |
| Med | roadmap:17; task:14,18 | `status: fail` 계약이 frontmatter status와 키 이름이 겹친다 | **적용**: Evidence 줄과 체크박스로 |
| Med | design:19; intent:18,73 | ≥90%를 측정할 수 없다. 로드되지 않은 tier와 "Trivial"을 참조한다 | **적용** |
| Med | task:32-37 | 24h를 측정할 수 없다. blocked 작업을 자동 삭제한다. `--dry-run`이 정의되지 않았다 | **적용** |
| Med | cleanup:26,34,64,81,90 | `--type docs`의 기본 동작이 불명확하다. 파일 삭제가 safe 등급에 있다 | **적용**: `--apply` 필수, 삭제는 승인 후 |
| Med | build:22,30-32,41 | 출력 디렉터리를 지어낸다. report 파일을 쓴다(RULES_DOCS는 inline-only) | **적용** |
| Med | troubleshoot:17 | 커밋 범위가 없다 | **적용**: 테스트 파일만 커밋, staged 변경이 있거나 default branch이면 질문 |
| Med | spec-panel:2 | 패널에 없는 Martin을 이름으로 든다 | **적용**: 실제 6개 렌즈 |
| Med | index-repo, document, index, estimate | 94%, ≥80%, 85% | **적용**: 측정한 바이트 수, 직접 센 개수, 신뢰 수준과 그 가정 |
| Med | estimate:49,54 | 이유 없이 시간 추정을 거절한다 | **적용**: 이유와 calibration 방법을 제시 |
| Med | document:30 / index:29,31 | API.md를 둘 다 덮어쓰고, README를 전체 재작성한다 | **적용**: 해당 부분만 수정하고 diff 표시 |
| Med | research:22,25,38,53 | RESEARCH_CONFIG가 주입되지 않는다. 출처 기준이 ≥2, ≥3, ≥1로 세 가지다 | **적용**: 전략의 의미를 본문에 넣고, 출처 기준을 ≥2로 통일(RESEARCH_CONFIG, deep-researcher 포함) |
| Med | business-panel:13 | 2-3명 vs 전체 9명 | **적용** |
| Med | help/sc:pm, agent/sc 예시 | pm을 "default"라고 부른다. agent 이름을 인자로 쓰는 예시가 있고 `deep-research`(없는 이름)를 쓴다 | **적용** |
| Med | save:16,64; load:18 | 로드되지 않는 reflect 필드를 참조한다. >30min, ctx 60% | **적용**: 필드를 본문에 쓰고, 관찰 가능한 조건으로 |
| Med | reflect:8,19 | 완료 판정 역할이 description과 본문에서 서로 반대다. 동의 없이 기록한다 | **적용**: 제안만 하고 동의 후에 기록 |
| Med | recommend:25-37 | 36개 중 11개만 다루고, plan 요청을 roadmap으로 보낸다. "how"는 거의 모든 질문에 걸린다 | **적용** |
| Med | auto-improve:59, 61 | 예시에 fable(동의 없는 과금)을 쓴다. JSON 인용이 깨졌다 | **적용** |
| Med | sc:13; help:13-16 | 파일 경로로 dispatch한다. help가 인자를 무시한다 | **적용**: Skill 도구로 호출, 인자별 흐름 |
| Med | research, reflect description | 커밋되는 문서를 쓰는데 Auto tier다(CHANGELOG 원칙상 on-request 대상) | **보류**: command-authoring은 research를 Auto 예시로 든다. 정책을 정해야 함 |
| Med | agent/pm/task | 서로를 구분하는 "Not for"가 없다 | 보류(P1) |
| Low | init 메뉴 9개 | RULES_INTERACTION 2차 수정으로 명령 고유 라벨이 허용된다 | 해당 없음. `--quick`(test에 없음)만 수정 |
| Low | analyze ↔ review description | 감사와 리뷰의 경계가 모호하다 | 보류 |
| Low | 다수 | 전보체("smart algo", "Git cmd + auto") | 손댄 파일 범위에서만 적용 |

## 출력 스타일 (plain-language.md)

| 심각도 | 근거 | 문제 | 처리 |
|---|---|---|---|
| Med | :9 우선순위 | 명령·모드가 정한 형식(Introspection 🎯⚡📊💡, BUSINESS_SYMBOLS)이 우선순위에 없다 | **적용**: 요청의 일부로 간주, 그 외에는 이모지 없음 |
| Med | :23, :48 | 허용 형식 목록에 표와 코드 서식이 없다 | **적용** |
| Med | :39 | "Ask only when the work cannot proceed"가 규칙이나 명령이 요구하는 확인과 경합한다 | **적용**: 규칙이나 명령이 확인을 요구하는 경우를 예외로 |
| Med | :29 | "not just X but Y" 금지가 실제 선택지 비교까지 막을 수 있다 | **적용**: 사용자가 실제로 비교하는 대비는 유지 |
| Med | :13 | 기존 파일과 프로젝트 관례의 언어가 빠졌다 | **적용** |
| Low | :21, :9 | 영어 전용 예시, 소스 코드 인용 오독 | :21 삭제(단어 예산) |
| Low (보류) | :39 "no offer of further work" | 명령의 handoff 제안과 경합할 수 있다 | d7b4150a에서 측정을 거쳐 넣은 규칙이라 유지 |

단어 수는 598에서 600으로 늘었다(상한 600). 중복된 점검 항목과 영어 전용 예시를 지워 예산을 확보했다.
