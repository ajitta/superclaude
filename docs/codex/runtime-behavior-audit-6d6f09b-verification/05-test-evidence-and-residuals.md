# Test evidence and residual verification

## 실행 결과

| 검증 | 결과 |
|---|---|
| 변경 영역 중심 unit selection | `855 passed` |
| 전체 suite `uv run pytest -q` | `2157 passed, 28 skipped, 4 deselected` |
| 프로젝트 기준선 대비 | regression 0 |

전체 suite 결과는 `AGENTS.md`에 기록된 기준선과 정확히 같다. 즉 이 문서의 발견은 기존 테스트 실패를 재분류한 것이 아니라, 현재 suite가 다루지 않는 경계 조건을 별도로 재현한 결과다.

## 직접 재현한 failure matrix

| ID | 조건 | 관찰 결과 | 자동 테스트 공백 |
|---|---|---|---|
| H-01 | 한 outer entry에 SC hook과 user hook 혼합 | force/uninstall이 user hook도 삭제 | SC/user가 outer entry별로 분리된 fixture만 검증 |
| H-02 | 같은 script의 다른 subcommand가 기존 등록 | 필요한 subcommand 누락, 기존 subcommand 중복 | 유리한 등록 순서만 검증 |
| H-03 | 현재 config에서 사라진 SC event + force | retired event 잔존 | 새 config에 있는 event만 검증 |
| H-04 | shipped와 obsolete hook 수만 동일 | `14/14` false green | identity 불일치 검증 없음 |
| I-01 | local 선택 뒤 EOF | user scope install, exit 0 | 최초 no-input과 명시적 decline만 검증 |
| I-02 | memory target이 regular file | install success, failed 0, directory 없음 | 정상 mkdir만 검증 |
| C-01 | 외부 CLI `--parallel`, `--link` | retired SC flag 안내 | SC typo positive case만 검증 |
| C-02 | 유효 command 뒤 unknown `/sc:` token | notice 없음, suppression 없음 | prompt당 첫 token만 검증 |
| R-01 | fresh project install + read-only prompt | 자체 cache untracked, Stop block | script 단위 test는 있지만 install→loader→git→Stop 연결 없음 |
| R-02 | harvest→promote→동일 transcript 재harvest | 같은 marker가 다시 pending 가능 | pending 상태에서의 반복 harvest만 검증 |

## 확인된 정상 동작

다음은 commit의 의도와 구현이 일치했다.

- session id A와 B가 같은 project에서 독립 context cache를 사용한다.
- clear/compact reset이 현재 session cache를 초기화하고 다른 session state를 무차별 삭제하지 않는다.
- 오래된 runtime state와 stale MCP fallback ledger가 pruning된다.
- 현재 shipped hook이 기존 settings의 같은 event에 빠져 있는 일반 non-force 경로에서는 새 hook이 추가된다.
- retired `/sc:workflow`와 단일 command typo 안내가 생성된다.
- `--think-hard`, `--parellel` 같은 의도된 retired flag 입력은 replacement notice를 낸다.
- 11개 command의 explicit-only description 구조가 유지된다.
- Stop hook의 JSON output schema와 `stop_hook_active` 재진입 gate는 Claude Code 계약에 맞다.

## 판정의 한계

이번 검증은 `src/superclaude/**`의 merge 내용과 그 직접 상호작용에 한정했다. 실제 Claude Code UI에서 일주일 동안 insight가 유용하게 누적되는지, model이 모든 자연어 command description을 어떤 확률로 해석하는지 같은 운영 관찰은 자동화하지 않았다.

따라서 다음 두 항목은 `human_needed`다.

1. P1/P2 수정 뒤 실제 Claude Code session에서 read-only, pre-dirty, code-changing 세션을 각각 수행해 Stop 요청 횟수와 pending 품질을 확인한다.
2. `/sc:git` 안전 문구를 통일한 뒤 destructive operation별로 별도 confirmation이 유지되는지 model eval을 수행한다.

## 권장 수정 순서

1. runtime state ignore/위치와 Stop baseline 판정을 함께 수정한다.
2. installer의 broad `click.Abort` fallback을 제거하고 취소 회귀 테스트를 추가한다.
3. hook 소유권을 inner-hook 단위로 바꾼 뒤 force, uninstall, inventory가 같은 identity 함수를 공유하게 한다.
4. `/sc:git` 승인 문구를 통일한다.
5. memory failure 전파, retired flag 문맥 gate, harvest ledger를 수정한다.
6. P3 진단·표시 항목을 정리한다.
