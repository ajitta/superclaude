---
status: draft
revised: 2026-10-20
---

# 남은 작업 (2026-10-20, v4.32.0 이후)

2026-10-19–20에 작업 세 갈래를 마쳤다.
- 설치·업그레이드 감사와 Windows 실기 검증: v4.30.5까지 릴리스.
- `CLAUDE_CONFIG_DIR` 지원(ADR-0002, v4.31.0).
- 압박 프로브 측정: hurry 프로브에서 sc-full 30/30 vs vanilla 20/30, p = 0.0004. 이때 eval arm 격리 결함 두 개를 찾아 고쳤다.
- 에이전트 감사: 24개 중 19개 폐기, 5개 유지(v4.32.0, [agent-roster-audit](../features/agent-roster-audit/README.md)).

지금 바로 할 승인된 작업은 없다. 남은 것은 다음 릴리스에 함께 나갈 변경, 다음 모델이 나올 때 할 일, 보류 항목, 정리 작업이다. 지난 목록은 [remaining-work-ajitta-2026-10-19](./remaining-work-ajitta-2026-10-19.md)이고, 이 문서가 그것을 대체한다.

항목마다 소유자 결정이 필요한지와 추천안(★)을 적는다. 세션 상태는 `.claude/memories/session_2026-10-20_master.md`의 Next actions에 같은 목록이 짧게 있다.

## 1. 다음 릴리스에 함께 나갈 것 — 완료

- [x] CHANGELOG `[Unreleased]`의 contributor용 항목 세 개(eval arm 격리, `sc-command-only` core import 제거, `probe-verify-claim` grader)는 v4.32.0에 함께 나갔다.

## 2. 압박 프로브 후속 — [pressure-readout](../features/pressure-readout/README.md)

- [ ] dictated-fix와 sunk-cost 프로브는 sonnet low에서 두 arm 모두 ceiling(9–10/10)이라 arm을 가르지 못한다. 결정: (a) regression guard로만 유지 / (b) 더 어려운 변형을 설계. ★(a). 다음 모델 canary에서 다시 본다.
- [ ] opus와 auto permission mode 측정. 결정: 할지 말지. ★보류. 한다면 격리된 harness에서 새로 pre-register한다. 측정을 시작하기 *전에* 커밋한다.
- [ ] 행렬 task `bugfix-scope-creep`은 아직 느슨한 `pytest|python -m pytest` grader를 쓴다. 결정: 시점. ★다음 모델의 행렬 run 때 맞춘다. 어차피 그때 기준선을 새로 잡는다.

## 3. 모델 세대 재감사(축 B)

- [ ] 다음 Claude 모델이 나오면 `superclaude-model-release` 절차로 진행한다. 이번에 처음으로 격리된 canary 기준선이 생겼다(`make canary-gates`, 2026-10-20, 7/7 gates). 그 전 run은 계정 콘텐츠가 실린 상태라 비교 기준으로 쓰지 않는다.

결정: 시점. ★다음 모델 출시 때. Fable 계열은 headless `claude -p`로 돌리지 않는다(사용 크레딧 청구, `evals/README.md`).

## 4. 보류 항목

- [ ] C-16: `19091b37` 시기의 `python .claude/hooks/x.py` 설치. install이 아무 말도 하지 않고, `session_init`이 두 번 돌고, uninstall이 명령 3개와 `hooks/*.py`를 남긴다([04a-handoff §2](../features/install-upgrade-audit/04a-handoff.md)).
- [ ] C-17: `bd356afa` → `52b5517e` 시기의 local/project hook 상태가 `~/.claude/.superclaude_hooks/`에 남는다. local·project uninstall은 그 디렉터리에 닿지도 않고 보고하지도 않는다.
- [ ] opus 후속 라운드(N2/N5): `purpose_before_action`의 opus D3a는 양(+)이지만 검정력이 부족했다(13/20 vs 8/20, p = 0.103). 그 run에는 계정 콘텐츠가 실려 있었다([purpose-opus 04](../features/purpose-opus/04-readout.md)의 caveat 참조). 재개한다면 격리된 harness에서 새로 pre-register하고, arm당 50–55회가 필요하다.
- [ ] "참조가 가리키는 파일을 연다" 규칙 문구 시험([purpose-generalization 04](../features/purpose-generalization/04-readout.md) §2).
- [ ] `origin/fix/plain-language-structure`: 10-10에 멈춘 문장 길이·구조 작업이다. 병합되지 않은 WIP 커밋 10개가 있다.

결정: 각각 재개 여부. ★모두 보류 유지. C-16/C-17은 해당 시기에 설치한 경우가 드물어 비용 대비 효과가 낮다. opus 라운드는 실행 비용이 크다.

## 5. 결정이 필요 없는 정리 작업

- [ ] Windows 설치를 최신 릴리스로 맞춘다(`superclaude doctor --scope <s>` → `make sync-*`). 소유자가 Windows 세션에서 한다.
- [ ] `docs/features/docs-ssot-audit/06-verify.md`가 약 29 KB로 Read 가드(30,000바이트)에 가깝다. 다음에 크게 덧붙일 때 `06b-…`로 나눈다.
- [ ] Windows에서 `0xC0000409` 중단이 다시 나오면 `git revert 3e64dc82`를 하고, `tests/unit/scripts/parallel_ab/`를 동시 부하에서 bisect한다(AGENTS.md Tests).

## 남겨 둔 알려진 한계

고치지 않기로 받아들인 동작이다. 근거는 [03-findings](../features/install-upgrade-audit/03-findings.md)의 C-20·C-21 행에 있다.

- 끝 줄바꿈이 없던 CLAUDE 파일은 install 후 uninstall을 거치면 줄바꿈이 하나 생긴다.
- `settings.json`의 한 줄 안 공백, 숫자 표기(`1e3`), 이스케이프(`\/`)는 다시 직렬화된다.
- 2026-10-20 이전의 eval 결과에는 claude.ai 계정 콘텐츠가 세션마다 다르게 실려 있었다. 다시 돌리지 않고, 격리된 run과 pool하지 않는다.
