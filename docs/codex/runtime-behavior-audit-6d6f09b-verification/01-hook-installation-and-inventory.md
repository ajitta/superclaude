# Hook installation and inventory

## P1 — 혼합 hook entry에서 사용자 hook이 삭제된다

관련 코드: `src/superclaude/cli/install_settings.py:131-158`, `:175-181`, `:291-335`

Claude settings의 한 outer entry는 하나의 `matcher`와 여러 inner hook을 가질 수 있다. `_is_superclaude_hook()`는 inner hook 중 하나라도 SuperClaude marker/path를 가지면 **outer entry 전체**를 SuperClaude 소유로 분류한다. 그 결과 다음 구성이 위험하다.

```json
{
  "matcher": "Edit",
  "hooks": [
    {"command": "python .../superclaude/scripts/prettier_hook.py", "_comment": "[superclaude]"},
    {"command": "npm run user-lint"}
  ]
}
```

격리 재현 결과:

- `_merge_hook_arrays(..., force=True)` 뒤에는 새 `prettier_hook.py`만 남고 `npm run user-lint`는 사라졌다.
- `uninstall_hooks_from_settings()` 뒤에는 settings 내용이 `{}`가 되었다.

이는 함수 docstring의 “preserving user hooks”와 merge의 “per-hook” 목표에 모두 어긋난다. 사용자가 직접 같은 matcher group에 hook을 합쳤거나 다른 설치기가 group을 정규화하면 실제 사용자 동작을 조용히 잃는다.

권고:

- 소유권 판정을 outer entry가 아니라 inner hook 단위로 옮긴다.
- `--force`는 SuperClaude inner hook만 교체하고 같은 entry의 사용자 inner hook은 보존한다.
- uninstall도 같은 분해 규칙을 사용한다.
- 혼합 entry의 선두·중간·말미에 사용자 hook이 있는 세 경우를 회귀 테스트로 추가한다.

## P2 — hook identity가 subcommand를 구분하지 못한다

관련 코드: `src/superclaude/cli/install_settings.py:35`, `:94-109`, `:188-205`

`_hook_script_id()`는 interpreter, 경로, 인자, timeout을 모두 버리고 `.py` 파일명만 identity로 삼는다. 경로 이동이나 option drift 시 중복 등록을 막는 장점은 있지만, 동일 script의 서로 다른 entry point도 같은 hook으로 취급한다.

다음 상태를 재현했다.

- 기존: `insight_writer.py pending-count-from-hook`
- shipped: `insight_writer.py harvest-from-hook`, `insight_writer.py pending-count-from-hook`
- merge 결과: `pending-count-from-hook` 두 개, `harvest-from-hook` 없음

Counter를 사용해 동일 script가 두 번 shipped되는 수량은 보존했지만 **어느 subcommand가 등록되었는지**는 보존하지 않는다. 현재 shipped config의 같은 event/matcher 안에는 이 조합이 없어 즉시 발생하는 기본 경로 결함은 아니지만, 함수 주석이 명시적으로 보장한다고 설명한 미래 확장 경로는 깨져 있다.

권고: identity를 `(matcher, script filename, stable entrypoint/subcommand)`로 만들고, 변경 가능 option만 별도로 정규화한다.

## P2 — `--force`가 retired event를 제거하지 않는다

관련 코드: `src/superclaude/cli/install_settings.py:257-280`

`merge_hooks_to_settings()`는 새 `hooks.json`에 존재하는 event type만 순회한다. 따라서 이전 버전의 SuperClaude hook이 이제 존재하지 않는 event에 남아 있으면 `--force`도 그 event를 보지 않는다.

재현:

- 기존 settings: SuperClaude `TeammateIdle` hook
- 현재 shipped config: `Stop` hook만 제공
- `force=True` merge 후 event: `Stop`, `TeammateIdle`

즉 `--force`가 “현재 shipped SuperClaude hook으로 교체”가 아니라 “현재도 존재하는 event 안에서만 교체”로 동작한다. retired hook이 계속 실행되거나 더 이상 배포되지 않는 script를 호출할 수 있다.

권고: force merge 전에 모든 기존 event를 순회해 SuperClaude inner hook을 제거하고, 비어 있는 entry/event를 정리한 뒤 현재 config를 넣는다. 사용자 hook은 앞 항목의 inner-hook 소유권 규칙으로 보존해야 한다.

## P3 — `hooks_registered`는 wiring이 아니라 개수만 비교한다

관련 코드: `src/superclaude/cli/install_inventory.py:73-98`, `:208-220`, `src/superclaude/cli/main.py:147-154`

`_count_shipped_hooks()`는 shipped hook 수를 세고 `_count_registered_hooks()`는 settings에서 SuperClaude로 분류된 hook 수를 센다. 두 집합의 identity 교집합은 확인하지 않는다. UI는 두 수가 같으면 `✅`를 표시한다.

14개의 현재 hook 대신 14개의 obsolete SuperClaude hook만 settings에 넣은 재현에서 결과는 `14/14`였다. 혼합 outer entry에서는 사용자 inner hook까지 SuperClaude 수에 포함될 수 있다. 따라서 이 진단은 Task 5가 찾으려던 “shipped hook이 실제로 wiring되었는가”를 보장하지 못한다.

권고:

- shipped와 registered의 normalized identity set/multiset을 비교한다.
- 출력은 `matched / shipped`로 계산하고 `missing`, `obsolete`, `duplicate`를 별도 표시한다.
- 수가 같지만 identity가 다른 경우와 한 mixed entry에 사용자 hook이 든 경우를 테스트한다.

## 정상 확인

기존 settings에 하나의 SuperClaude hook이 있고 같은 event에 새로운 **다른 script**가 추가되는 일반 non-force 경로는 기존 entry를 보존하면서 누락 hook을 추가한다. 완전히 동일한 outer entry의 dedup도 idempotent하다. 문제는 소유권 또는 identity가 outer group과 script filename보다 세밀해야 하는 경계에서 발생한다.
