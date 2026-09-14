# Runtime state and INSIGHT pipeline

## P1 — runtime cache가 tree를 dirty로 만들고 Stop hook을 스스로 발화시킨다

관련 코드:

- `src/superclaude/utils/__init__.py:82-107`
- `src/superclaude/scripts/context_loader.py:57-71`, `:802-827`
- `src/superclaude/cli/install_git_exclude.py:45-63`
- `src/superclaude/scripts/insight_writer.py:500-556`
- `src/superclaude/hooks/hooks.json:140-147`

project/local scope의 `hook_state_dir()`는 `<project>/.claude/.superclaude_hooks`다. `context_loader`는 import 시 이 directory를 만들고 prompt 처리 중 session cache를 기록한다. 그러나 local exclude 목록에는 이 경로가 없고 project scope에도 별도 ignore 처리가 없다.

새 Stop hook의 “세션이 코드를 바꿨는가” proxy는 `git status --porcelain`에 출력이 있는지만 본다. 따라서 framework 자신의 untracked cache가 user code change로 취급된다.

fresh repo 격리 재현:

1. project-scope install 산출물을 baseline commit한다.
2. read-only prompt `hello`로 `context_loader`를 실행한다.
3. `git status --porcelain`은 `?? .claude/.superclaude_hooks/`를 출력한다.
4. 같은 session id로 `insight_writer.py request-from-hook`를 실행한다.
5. `{"decision":"block", ...}`가 출력된다.

즉 사용자가 파일을 바꾸지 않은 세션도 종료 시 추가 응답을 강제받는다. Stop hook의 top-level `decision: block`과 `reason` 형식 자체는 [Claude Code hook reference](https://code.claude.com/docs/en/hooks)에 맞지만, block 여부를 만드는 upstream 상태가 잘못되었다.

권고:

- rebuildable runtime state를 worktree 밖에 둔다. worktree 안에 둘 이유가 있다면 project/local 모두 `.git/info/exclude` 등에 `.claude/.superclaude_hooks/`를 등록한다.
- `_working_tree_changed()`가 SuperClaude 자체 state 경로를 제외하도록 방어를 추가한다.
- fresh committed repo에서 read-only prompt 후 status가 clean이고 Stop output이 비어 있음을 end-to-end test로 고정한다.

## P2 — pre-existing dirty tree와 one-shot guard가 세션 변화 판정을 왜곡한다

관련 코드: `src/superclaude/scripts/insight_writer.py:500-556`

`_working_tree_changed()`는 현재 tree가 dirty인지 묻지, 해당 session이 tree를 바꿨는지는 묻지 않는다. 주석도 이를 proxy로 인정한다. 더 중요한 점은 첫 요청 전에 guard를 기록하고 같은 session에서는 다시 묻지 않는다는 것이다.

그 결과:

- 세션 시작 전부터 dirty인 repo에서 첫 read-only 답변이 INSIGHT 요청을 소비한다.
- 사용자가 “이번에는 없음”이라고 답한 뒤 같은 session에서 실제 코드를 수정해도 guard 때문에 다시 요청하지 않는다.
- 앞 P1의 자체 cache dirty가 있으면 이 오판이 project/local 설치의 정상 시작 경로가 된다.

권고: SessionStart에서 baseline status/fingerprint를 session state로 저장하고 Stop에서 diff한다. one-shot은 “qualifying change 이후 요청 완료”에 대해 기록해야 하며 단순히 첫 dirty 관찰에 소비하면 안 된다.

## P2 — assistant 전체 수확은 오탐과 재수확을 만든다

관련 코드: `src/superclaude/scripts/insight_writer.py:303-351`, `:430-464`

새 producer를 가능하게 하기 위해 harvester는 transcript의 모든 assistant record에서 inline `INSIGHT:`를 찾는다. Stop request 자체는 sentinel로 제외하지만, marker가 실제 요청에 대한 최종 한 줄인지 연결하지 않는다.

따라서 다음 텍스트도 pending entry가 될 수 있다.

- 문서나 코드 예시로 설명한 `INSIGHT: ...`
- 이전 답변을 인용한 내용
- 사용자가 원하지 않은 assistant의 중간 서술

또 dedup UUID는 현재 pending 파일에서만 읽는다. promote가 성공하면 해당 pending row를 제거하므로 다음 순서가 가능하다.

```text
PreCompact harvest → promote → SessionEnd harvest of the same transcript
```

마지막 단계에서 같은 marker UUID가 pending에 더 이상 없으므로 재수확된다. 이 dedup 구조는 기존에도 있었지만 assistant 자동 producer가 추가되면서 정상 사용 경로에서 노출될 가능성이 커졌다.

권고:

- Stop hook 요청 이후의 `last_assistant_message` 또는 request/response correlation을 사용해 의도된 producer 출력만 수확한다.
- harvested UUID ledger를 pending과 분리해 promotion 뒤에도 유지하거나, durable insight record에 source UUID를 보존해 중복 검사한다.
- 설명용 marker, sentinel과 실제 marker가 같은 record에 있는 경우, harvest→promote→harvest 순서를 회귀 테스트한다.

## 정상 확인 및 잔여 검증

- session id별 context cache 파일 분리와 clear/compact reset은 테스트 및 정적 연결에서 정상이다.
- 7일 경과 state pruning과 MCP fallback ledger 정리는 현재 session의 state를 보존한다.
- Stop 재진입 시 `stop_hook_active` gate는 반복 block을 막도록 연결되어 있다.
- 구현 계획 `docs/features/runtime-behavior-audit/05-plan.md`의 Task 11 체크리스트와 실제 real-session success criterion은 아직 미완료 상태로 남아 있다. producer가 “발화한다”는 사실과 “정확한 때에 유용한 insight가 누적된다”는 것은 별도 검증이 필요하다.
