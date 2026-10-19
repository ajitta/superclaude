---
status: draft
revised: 2026-10-19
---

# 남은 작업 (v4.30.4 이후)

2026-10-19에 v4.30.2–v4.30.4 세 번의 릴리스로 설치·업그레이드 감사(축 C)의 S1/S2 결함, C-20/C-21, 문서 ↔ SSOT 감사(축 D), research hop 수 정리를 마쳤다. 이 VM에서 할 수 있는 승인된 작업은 남아 있지 않다. 남은 일은 Windows 실기 검증과 그 결과를 기다리는 결정 두 개, 다음 모델 출시 때의 재감사, 보류 항목이다.

각 항목은 소유자 결정이 필요한지와 추천안(★)을 적는다. 세부 근거는 링크된 문서에 있고, 세션 상태는 `.claude/memories/session_2026-10-19_master.md`의 Next actions가 같은 목록을 짧게 담는다.

## 1. Windows 실기 검증 — 소유자만 가능

- [x] Windows 설치를 4.30.4로 맞춘다. `superclaude doctor --scope <s>`를 먼저 보고, `make sync-*`로 갱신한다. (local scope는 이미 4.30.4, drift 없음)
- [x] `scripts/install-audit-windows.ps1`을 Windows PowerShell 5.1과 `pwsh` 7에서 한 번씩 돌리고, 출력된 sandbox의 `results.md`를 붙여 넣는다. 이 스크립트는 Linux에서 작성되어 한 번도 실행된 적이 없으므로, 스크립트 오류는 결함이 아니라 스크립트 버그로 보고한다.
- [x] W1–W7을 확인한다(약 45분). 질문과 판정 기준은 [04a-handoff §1c](../features/install-upgrade-audit/04a-handoff.md).

**결과 (2026-10-19, [07-windows-run](../features/install-upgrade-audit/07-windows-run.md)):** 새 S2 결함 W-3이 나왔다. Windows에서 install/uninstall이 `.git/info/exclude` 전체를 CRLF로 다시 쓰던 문제로, 지금은 고쳤다. 스크립트 버그 S-1도 고쳤다. W1–W5는 결함 없음. W6에서 Claude Code는 BOM 붙은 settings를 받아들였고, 그래서 3번(BOM 허용)도 반영했다. W7에서는 settings, 컴포넌트, user `CLAUDE.md`가 모두 `CLAUDE_CONFIG_DIR`을 따른다는 것을 확인했다. **v4.30.5로 릴리스했다** (merge 5705e79a, stable = ed0dd74b).

결정: 언제 할지. ★다음 Windows 세션의 첫 작업. W6과 W7 결과가 2·3번의 입력이다.

이미 끝난 부분: §1a의 dispatch 전용 Windows CI 작업은 v4.30.2 master(run 39218794149)에서 green이다. 실패 기록과 W-2(테스트 fixture 결함)는 04a §1a와 [03-findings](../features/install-upgrade-audit/03-findings.md)에 있다.

## 2. C-15 — `CLAUDE_CONFIG_DIR` 경고 범위

- [x] W7 결과를 보고 결정한다. W7 결과: settings, 컴포넌트, user `CLAUDE.md`가 모두 `CLAUDE_CONFIG_DIR`의 디렉터리에서 읽힌다. → (b)로 결정했고 [ADR-0002](../adr/0002-user-scope-follows-claude-config-dir.md)로 구현했다(`feat/claude-config-dir`).

지금은 user scope의 install과 doctor만 경고한다. uninstall은 경고하지 않고, `$CLAUDE_CONFIG_DIR/.claude.json`의 user-scope MCP 서버도 다루지 않는다. W7이 "Claude Code는 그 변수의 디렉터리를 읽는다"를 확인하면 Q15 (a) ADR(`get_base_path`가 변수를 따름)의 근거가 된다.

결정: (a) uninstall과 MCP reader로 경고 확장 / (b) Q15 (a) ADR을 써서 변수를 따르게 변경 / (c) 그대로. ★W7 결과를 본 뒤 결정(그 전에는 (c)).

## 3. BOM이 있는 설정 파일 — W6 결과에 따라서만

- [x] W6 결과를 기록한다. → Claude Code가 BOM을 받아들였다. settings와 CLAUDE 파일의 BOM을 허용하고, 쓸 때도 BOM을 유지하도록 바꿨다(`fix/windows-file-fidelity`).

지금 install은 BOM이 있는 settings·CLAUDE 파일을 거부하고, doctor도 같은 이유로 실패를 낸다. W6에서 Claude Code가 BOM 붙은 `settings.json`을 받아들인다고 나오면 읽기를 `utf-8-sig`로 완화할 수 있다(plan Q16). `info/exclude`의 BOM 거부는 소유자가 유지로 결정했다(04a §3).

결정: W6이 수용을 보여 줄 때만. ★그 전까지 거부 유지.

## 4. 모델 세대 재감사(축 B)

- [ ] 다음 Claude 모델이 나오면 `superclaude-model-release` 절차로 진행한다.

결정: 시점. ★다음 모델 출시 때. Fable 계열은 headless `claude -p`로 돌리지 않는다(사용 크레딧 청구, `evals/README.md`).

## 5. 보류 항목

- [ ] C-16: `19091b37` 시기의 `python .claude/hooks/x.py` 설치. install이 아무 말도 하지 않고, `session_init`이 두 번 돌고, uninstall이 명령 3개와 `hooks/*.py`를 남긴다. CHANGELOG 업그레이드 노트로 Q14 (b)는 충족됐다.
- [ ] C-17: `bd356afa` → `52b5517e` 시기의 local/project hook 상태가 `~/.claude/.superclaude_hooks/`에 남는데, local·project uninstall이 닿지도 보고하지도 않는다.
- [ ] opus 후속 라운드(N2/N5): `purpose_before_action`의 opus D3a 효과는 양(+)이지만 검정력이 부족했다(13/20 vs 8/20, p = 0.103). 사전 등록한 새 라운드에 arm당 50–55회가 필요하다([purpose-opus 04-readout](../features/purpose-opus/04-readout.md)).
- [ ] "참조가 가리키는 파일을 연다" 규칙 문구 시험: sonnet이 참조된 파일을 열지 않는 문제([purpose-generalization 04-readout](../features/purpose-generalization/04-readout.md) §2).
- [ ] `origin/fix/plain-language-structure`: 10-10에 멈춘 문장 길이·구조 작업, 병합되지 않은 WIP 커밋 10개.

결정: 각각 재개 여부. ★모두 보류 유지. C-16/C-17은 해당 시기 설치가 드물어 비용 대비 효과가 낮고, opus 라운드는 실행 비용이 크다.

## 6. 결정이 필요 없는 정리 작업

- [ ] `docs/features/docs-ssot-audit/06-verify.md`가 약 29KB로 Read 가드(30,000바이트)에 가깝다. 다음에 크게 덧붙일 때 `06b-…`로 나눈다.
- [ ] Windows `0xC0000409` 중단이 다시 나오면 `git revert 3e64dc82` 후 `tests/unit/scripts/parallel_ab/`를 동시 부하에서 bisect한다(AGENTS.md Tests).

## 남겨 둔 알려진 한계

수정하지 않기로 받아들인 동작이다. 근거는 [03-findings](../features/install-upgrade-audit/03-findings.md) C-20·C-21 행.

- 끝 줄바꿈이 없던 CLAUDE 파일은 install 후 uninstall을 거치면 줄바꿈 하나가 생긴다.
- `settings.json`의 한 줄 안 공백, 숫자 표기(`1e3`), 이스케이프(`\/`)는 다시 직렬화된다.
