---
status: implementing
revised: 2026-10-07
---

# AI-Native SDLC Playbook 대조 분석

**대상.** Anthropic "The AI-Native SDLC Playbook"(Louis Claxton, Applied AI; 'https://claude.com/resources/articles/the-ai-native-sdlc-playbook', PDF 다운로드판을 markitdown으로 변환해 읽음) 6단계 14개 플레이 vs SuperClaude 4.21.0(`src/superclaude/hooks/hooks.json`, `core/rules/RULES_DOCS.md`, 커맨드 flow, `evals/`, `.github/workflows/test.yml`).

**결론.** 플레이북의 핵심 주장 "각 단계는 커밋된 산출물로 끝나고 다음 단계가 그것을 읽는다"를 SuperClaude는 이미 구조로 갖고 있다(`docs/features/<slug>/01-discovery → 04-design → 05-plan`, workflow_gates). brainstorm과 plan 사이의 필수 /sc:review, 위임 결정 감사, 블래스트 반경별 검증 사다리(R15), 서브에이전트 패킷 규칙은 플레이북보다 더 나간다. 차이는 세 군데에 몰려 있다. 플레이북은 규칙마다 결정적 집행(훅, CI 게이트)을 붙이는데 SuperClaude는 상당수가 프로즈 규칙에 머문다. 산출물 체인은 있지만 수동 호출이다(의도적, 아래 전제). 플레이마다 측정 지표를 두는 플레이북과 달리 자기 워크플로를 재는 지표가 없다(필요성 미통과, 제외).

## 전제 (사용자 결정, 2026-10-07)

1. **단계별 수동 호출은 의도다.** 자동 연쇄가 의도와 다른 결과와 오버엔지니어링을 낳는다고 보고, 사람 판단을 각 게이트에 두는 것이 프레임워크의 목적이다. 플레이북도 "처음엔 각 단계를 손으로 프롬프트한다"를 시작점으로 두며, SuperClaude는 그 시작점을 최종 상태로 택했다. 따라서 게이트를 없애거나 건너뛰는 개선은 제외하고, 게이트에서 사람이 보는 산출물의 품질을 높이거나 통과 조건을 결정적으로 확인하는 개선만 남긴다.
2. **구독 계정이라 ANTHROPIC_API_KEY가 없다.** headless 작업(evals, canary, auto-improve)은 로컬에서 `claude -p` OAuth로 돈다. API 키가 필요한 CI 워크플로는 불가.
3. **Trivial 작업은 게이트를 지나지 않는다.** README 티어 표(Trivial = 직접 편집), RULES_QUALITY `checklist_scaling`(Small = 증거만), `verification_ladder` Level 0·1, 모든 커맨드 description의 부정 게이트가 이미 그렇게 한다. 개선 항목은 어느 것도 Trivial·Small에 새 게이트를 얹지 않는다.
4. **CC plan mode는 더 이상 기본이 아니다.** 2026-08-14부터 Pro/Max/Team 새 세션은 auto mode가 기본(Anthropic 공지), v2.1.283부터 전 플랜 기본. 9월 23일 Claude Code 팀이 plan mode 제거를 검토했다가 커스터마이즈 가능한 내장 mod로 유지로 선회. 플레이북 Build 플레이의 "plan mode를 기본 시작점으로"는 이 변화 전 문장이다. SuperClaude의 대응물은 CC 모드가 아니라 /sc:plan이 커밋하는 계획 문서이므로 영향 없음. 단, auto mode의 시스템 리마인더("Execute immediately … do not enter plan mode unless explicitly asked")가 plan mode 리마인더를 이기는 사례가 여러 건 보고돼(anthropics/claude-code #51630, #53276 등), 프로즈로만 존재하는 /sc:* 체크포인트에도 같은 힘이 작용할 수 있다. PreToolUse 훅과 permission ask/deny 규칙은 auto mode에서도 집행된다.

## 플레이별 대조

| 플레이 | 상태 | SuperClaude 대응물 | 차이 |
|---|---|---|---|
| 1 intent.md 캡처 | 부분 | /sc:brainstorm → 01-discovery, Resolved Decisions 표, 자기검토 게이트 | 분석 전에 요청자의 말로 적는 고정 골격(문제·목표·영향 대상·제약·미결 질문)이 없음. brainstorm은 들어가는 순간 재해석함 → `/sc:intent` 신설(`../intent-command/05-plan.md`) |
| 2 요구+설계 단일 세션 | 부분 | /sc:design → 04-design, R18 필요성 테스트 | `--from`이 없어 discovery 문서를 공식 입력으로 받지 않음. "정책 충돌 지점" 필수 섹션 없음(evals는 이미 `conflict` 지표로 이 행동을 잼). 조직 정책 스킬 슬롯 없음(팀 전제, 제외) |
| 3 plan mode 기본, plan.md | 부분 | /sc:plan TDD 템플릿, `--plan` 소비 | 템플릿에 Risks·채택 안 한 대안·Proof 없음(FLAGS의 5줄 `--plan`에는 risks가 있어 불일치). "plan을 심문하라" 단계 없음. 구현이 계획에서 벗어날 때 같은 커밋에서 plan 갱신 규칙·검사 없음 — plan-checklist-vs-status gotcha로 이미 실패 관측(status complete에 0/15 체크) |
| 3 auto mode | 미충족 | --safe-mode, --validate | 의도상 제외. 대신 auto mode 아래 프로즈 게이트 생존 여부를 측정(개선 8) |
| 3 CLAUDE.md | 충족 | R19 gotcha 캡처, durability routing, /sc:reflect 90일 가드닝 | "두 번 틀리면 CLAUDE.md"와 일치. 이 저장소의 gotchas/general.md 항목은 문단 길이라 "한 페이지" 원칙과 어긋남 |
| 3 스킬 = 제도 지식 | 부분 | commands(워크플로), agents(페르소나), `.claude/rules`(경로 조건부) | 정책 스킬 자리는 CC 표준 `.claude/skills/`가 이미 있음. 프레임워크가 할 일 없음 |
| 3 빌드 훅 가드레일 | 부분 | destructive_guard(block+사유, warn tier), loop_guard, prettier_hook, file_size_guard | 보호 경로 편집 차단·자격증명 유출 가드 없음. prettier는 JS/TS만. test_runner_hook은 편집마다 전체 테스트(플레이북은 "무거운 검사는 커밋/PR에") — 비동기·opt-out이고 보고된 문제 없어 보류 |
| 3 병렬 세션·서브에이전트 | 부분 | 23 agents, RULES_DELEGATION 워크트리 안내 | simplifier(refactoring-expert, simplicity-guide)·researcher(repo-index)는 있으나, 앱을 실행해 plan과 대조하고 "고치지 않고 보고만" 하는 verifier 없음. self-review는 Bash가 없어 실행해 대조할 수 없음 |
| 4 피드백 루프 | 충족 | R15 사다리, R20 성공 기준, R21 실패 기록, "/sc:test → done: 실제 출력 필수" | troubleshoot `--fix`의 실패 테스트 우선은 있으나 수정 중 테스트 파일 편집을 막는 훅 없음 |
| 4 지속 평가 CI | 부분 | evals/ 4-arm + canary 14 task, 7 hard gate, 9 지표, `claude -p` | 수동 전용. core/rules·hooks 변경에 반응하지 않음. gotcha·insight → eval probe 경로가 수동. CI 연결은 전제 2로 불가 |
| 5 PR 리뷰 루프 | 부분 | /sc:review 2D(spec 충실도+품질), Critical/Important/Suggestion | "이 diff가 항상 로드되는 문서를 낡게 했는가" 점검 없음. R19는 사용자 교정에만 반응. 저장소 수준 REVIEW.md와 PR babysit 루프는 조직용·제외 |
| 5 승인 게이트 훅 | 부분 | destructive_guard block/warn | 모든 가드가 env로 끌 수 있어 자문적. 개인 프레임워크에서는 맞음 |
| 5 CI/CD 내 claude -p | 미충족 | auto-improve 로컬 headless | 범위 밖 |
| 6 루프 닫기 | 부분 | insight 파이프라인(PreCompact/SessionEnd 수확, pending 알림), memory_staleness | lessons 파일 역할은 함. "사건 → eval 케이스" 규칙 없음 |
| 횡단: 측정 | 미충족 | 없음 | 없어도 깨지는 것 없음. docs/features 프론트매터·git 로그로 필요 시 직접 계산. 제외 |

## 정제된 개선 항목

우선순위 순. 각 항목은 R18 필요성 테스트("없으면 실제로 무엇이 깨지는가")를 통과한 것만 남겼다. 어느 것도 Trivial·Small 티어에 새 게이트를 얹지 않는다.

1. **`/sc:intent` 커맨드** (Stage 1). 의도의 원본 기록이 없어 /sc:review의 spec fidelity가 이미 해석된 spec과만 비교한다. brainstorm.md 스스로 "승인된 spec에서 3건의 치명적 반전"을 기록했고 위임 결정 감사가 생긴 이유도 원래 의도가 흐려져서였다. 계획: `../intent-command/05-plan.md`.
2. **계획 편차 동기화 검사** (Stage 3). /sc:implement Integrate 단계에 "Deviations" 기록, `status: complete`인 plan 문서에 미체크 박스가 남으면 red가 되는 단위 테스트 하나. 자동화가 아니라 게이트에서 사람이 믿고 볼 상태 표시의 보증.
3. **/sc:plan 템플릿에 Risks·채택하지 않은 대안·Proof 섹션과 심문 단계** (Stage 3). 지금은 Goal/Architecture/Tech Stack/Tasks뿐. Risks·대안은 Small에서 한 줄 또는 "none" 허용(checklist_scaling의 "Small은 리스크 매트릭스 생략"과 맞춤), Proof는 항상 명령과 기대 출력을 적는다. Interrogate 단계를 새로 두어 "무엇이 깨질 수 있나, 가장 위험한 단계는, 왜 다른 길을 버렸나"를 푸터에 답한다.
4. **/sc:design에 `--from`과 "우려 지점(정책 충돌)" 필수 섹션** (Stage 2).
5. **verifier 에이전트** (Stage 3·4). 읽기 전용 도구(Read·Grep·Glob)와 Bash만, report-only, 앱이나 테스트를 실행해 plan 문서와 대조한 보고. /sc:test 단계에서 사용자가 명시적으로 부른다. "/sc:test → done: 실제 출력 필수" 게이트의 증거 생산자.
6. **훅 2종** (Stage 3·4). 2026-10-07 결정으로 훅은 만들지 않는다. 테스트 파일 잠금 훅은 구현·리뷰까지 마쳤다가(3362816e) 걷어냈다. 경로 규칙이 언어 관례에 묶여 어떤 환경에서나 쓰이는 프레임워크에 맞지 않고, 모델 능력이 프로즈 규칙으로 충분하다고 판단했다. 남은 것은 /sc:troubleshoot의 fix-not-test gotcha(수정 중 실패 테스트는 읽기 전용, 테스트가 틀렸으면 이유를 적고 재검토)와 실패 테스트 커밋 규칙이다. 보호 경로 편집 차단도 같은 이유로 보류.
7. **canary를 릴리스 전 수동 게이트로** (Stage 4, 로컬 `claude -p`). `src/superclaude/core`나 `hooks.json`이 지난 `v*` 태그 이후 바뀌었으면 `make release`가 거부하고, 사람이 `make canary-gates`(하드 게이트가 있는 과제만, sonnet, low effort) 보고서를 읽은 뒤 `CANARY_OK=1`로 다시 돌린다. 전체 `--canary`는 모델 릴리스용. R19 gotcha 캡처·insight 승격 시 "canary probe로도 추가할까" 한 줄 → "사건마다 eval 하나".
8. **canary에 auto mode 조건 추가** (전제 4의 측정). run_eval.py는 `--allowedTools`만 넘기고 permission mode를 지정하지 않는다. `conflicting-constraints`·`problem-statement-not-request` 프로브를 `--permission-mode auto`로도 돌려 항상 로드되는 규칙의 멈춤 동작(문제 진술이면 보고 후 멈춤, 충돌하는 프로젝트 규칙 표면화)이 살아남는지 잰다. 이 프로브들은 `/sc:` 커맨드를 부르지 않으므로 커맨드 체크포인트는 `implement-checkpoint` 프로브(`/sc:implement`로 5파일 이름 변경, 3파일 초과 승인 대기)가 따로 잰다. brainstorm "확인 없이 진행 금지"와 task의 체크포인트는 아직 재지 못한다. 붉으면 그때 어느 체크포인트를 훅으로 옮길지 정한다. 측정 전에 훅을 늘리는 것은 과하다.
9. **/sc:review 세 번째 차원** (Stage 5). "이 변경이 항상 로드되는 문서를 낡게 했는가"를 소견 범주로, R19 발동 조건을 리뷰에서 같은 소견이 두 번째 나온 경우로 확장. 기존 규칙의 조건 한 줄 수정.
10. **낮은 우선순위**: gotcha 항목 길이 예산.

## 진행 상태 (2026-10-07, 브랜치 docs/intent-command-plan)

| 항목 | 상태 | 커밋 |
|---|---|---|
| 1 /sc:intent | 완료 (남은 것: CHANGELOG는 버전 범프 커밋, Save 경로 대화형 확인은 ../intent-command/05-plan.md Task 7 Step 4) | 7de4b521 |
| 2 계획 편차 검사 | 완료 (Deviations 규칙 + tests/unit/test_plan_checklist.py) | da4a2f12 |
| 3 /sc:plan 푸터·Interrogate | 완료 | da4a2f12 |
| 4 /sc:design --from·Concerns | 완료 | da4a2f12 |
| 5 verifier 에이전트 | 완료 (/sc:test Verify 단계에서 명시 호출) | 3362816e |
| 6 테스트 파일 잠금 훅 | 철회 (훅 제거, 프로즈 규칙 fix-not-test만 유지) | 3362816e → c147b80c |
| 7 canary 릴리스 게이트 | 완료 (make release, CANARY_OK=1; 비용 결정으로 게이트는 `make canary-gates` 4개 과제·sonnet·low effort, 전체 `--canary`는 모델 릴리스 때만) | 7cf07537 + 611244e7 |
| 8 canary --permission-mode | 완료 (측정 실행은 아직) | 3362816e |
| 9 /sc:review Dim 3·R19 확장 | 완료 | da4a2f12 |
| 10 gotcha 길이 예산 | 완료 (항목당 320자, `tests/unit/test_gotcha_budget.py`; 3개 파일 24.6KB→13.5KB, 유실 지적 15건 복원) | c01112fc |

## 제외한 항목과 이유

- evals CI 워크플로: API 키 없음(전제 2). 7번으로 대체.
- auto mode·permissions.allow 안내, 수락된 산출물이 다음 단계를 발동하는 트리거: 승인 프롬프트를 줄이는 방향 자체가 의도와 반대(전제 1).
- README에 CC plan mode로 세션을 시작하라는 안내: 전제 4.
- 저장소 수준 리뷰 정책 파일(REVIEW.md), PR babysit 루프: 관리형 Code Review·claude-code-action이 읽는 조직용 장치. /sc:review 흐름이 이미 그 역할.
- 지표 산출 도구: 없어도 깨지는 것 없음.
- 조직 정책 스킬 슬롯: 정책 소유자가 있는 팀 환경 전제. CC 표준 `.claude/skills/`가 이미 자리.
- test_runner_hook 범위 축소: 비동기·opt-out, 보고된 문제 없음.
- Maintain 단계에서 사고를 intent로 되돌리는 경로: 소비자 없음.

## 바꾸지 말 것

brainstorm→review 필수 게이트, 위임 결정 감사, 검증 사다리, 위임 패킷 규칙, hard gate가 있는 eval 하네스. 플레이북에 없는 장치이고 "advisory 규칙 뒤에 결정적 집행을 두라"는 플레이북의 방향과 같은 편이다.

## 출처

- Anthropic, "The AI-native SDLC playbook" (Louis Claxton, 2026-08-21), 'https://claude.com/resources/articles/the-ai-native-sdlc-playbook' (PDF 다운로드 제공; Claude Academy 코스 'https://academy.claude.com/courses/ai-native-sdlc-playbook/introduction')
- Anthropic, "Auto mode is now the default in Claude Code for Pro, Max, and Team plans", 2026-08-07, 'https://claude.com/blog/auto-mode-default-in-claude-code'
- Claude Code Docs, What's new Week 32 (2026-08-03~07), 'https://code.claude.com/docs/en/whats-new/2026-w32'
- Anthropic Engineering, "How we built Claude Code auto mode", 2026-03-25, 'https://www.anthropic.com/engineering/claude-code-auto-mode'
- A. Aleinikov, "Claude Code Modes Compared: Why Plan Mode Died", 2026-09-28
- aiidelist, "Claude Code vs Google Antigravity: The Plan Mode Split", 2026-09-27 (9월 23~24일 plan mode 제거 검토와 선회)
- anthropics/claude-code issues #51630, #53276 (auto mode 리마인더가 plan mode를 덮는 사례)
