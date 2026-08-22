# Command contracts and resolution

## P1 — `/sc:git` invocation과 파괴 작업 승인이 혼동된다

관련 코드: `src/superclaude/commands/git.md:2`, `:75-84`

frontmatter description은 사용자가 `/sc:git`을 명시적으로 입력하면 `push --force`, `reset --hard`, `rebase`를 “approves”한다고 쓴다. 같은 파일의 `<bounds>`는 destructive operation에 confirm이 필요하다고 하고, `<approval_required>`도 세 작업을 다시 열거한다.

이 두 계약은 동시에 참일 수 없다. `/sc:git status`나 인자 없는 `/sc:git`은 command 사용 승인이지 history rewrite 승인일 수 없다. 특히 “wrong fire cost a revert”라는 표현은 force push나 hard reset이 단순 revert로 항상 복구된다는 잘못된 안전 인상도 준다.

`disable-model-invocation: true`는 모델의 자동 호출을 막지만, 사용자가 command를 명시한 뒤 모델이 frontmatter를 어떻게 해석할지에 대한 충돌은 해결하지 않는다.

권고:

- description의 “approves history-rewriting ops”를 제거한다.
- command invocation은 `/sc:git` workflow 사용만 승인하며, destructive sub-operation은 해당 작업과 target을 명시한 별도 확인이 필요하다고 한 문장으로 통일한다.
- feature branch force push, main force push, reset, rebase 각각에 approval test/eval을 둔다.

## P2 — retired flag 안내가 외부 CLI option을 오인한다

관련 코드: `src/superclaude/scripts/context_loader.py:321-377`

`resolve_flags()`는 prompt 안의 모든 `--name`을 SuperClaude flag 후보로 검사한다. 이 merge에서 retired flag의 fuzzy match를 기존 unknown-flag 처리보다 먼저 추가하면서 일반 CLI option까지 적극적으로 retired SuperClaude flag로 해석한다.

실제 결과:

| 입력 일부 | 출력된 잘못된 안내 |
|---|---|
| `cargo test --parallel` | `--parallel`이 retired됐으니 `--delegate`/`--concurrency`를 쓰라는 안내 |
| `curl --link ...` | `--link`가 `--think` 같다는 안내 |
| `pytest --no-parallel` | `--parallel` 오타라는 안내 |
| `tool --parallelism 4` | `--parallel` 오타라는 안내 |

prompt가 외부 명령 실행을 요청하는 것인지 SuperClaude behavior flag를 쓰는 것인지 구문적 경계가 없다. 사용자가 유효한 build/test option을 에이전트용 flag로 잘못 바꾸도록 유도할 수 있다.

권고:

- `/sc:` invocation 또는 명확한 SuperClaude flag 구간에서만 retired/fuzzy 검사를 수행한다.
- 최소한 shell command/code fence 내부의 option은 제외한다.
- fuzzy retired match는 exact retired match보다 훨씬 보수적인 threshold와 문맥 gate를 사용한다.
- 대표 외부 도구의 `--parallel`, `--link`, `--scope`, `--plan` 같은 충돌 option을 negative test로 추가한다.

## P3 — 여러 `/sc:` token 중 첫 번째만 검증한다

관련 코드: `src/superclaude/scripts/context_loader.py:398`, `:421-453`, `:829-841`

`resolve_command_name()`는 `_COMMAND_TOKEN_RE.search()`로 첫 match 하나만 본다. 첫 token이 유효하면 즉시 정상 반환하므로 뒤의 unknown/retired command는 안내도, context suppression도 받지 않는다.

재현:

```text
known = {analyze, review}
prompt = /sc:analyze then /sc:zzzzzz
result = ([], False)
```

일반적으로 한 prompt에 한 command만 쓰는 사용 패턴에서는 영향이 작다. 그러나 chained instruction 또는 command 사용 예시를 포함한 요청에서는 “unknown name은 실제 command처럼 보이면 안 된다”는 함수 계약이 일부 token에만 적용된다.

권고: 모든 token을 순회해 token별 notice를 만들고, suppression 정책을 명시한다. 단순히 전체 prompt의 command context를 끄기보다 unknown token만 제거한 trigger prompt를 만드는 편이 안전하다.

## Explicit-only 변경에 대한 판정

11개 command description의 explicit-only 문구와 구조 테스트는 적용됐다. 다만 `git`을 제외하면 강제 장치가 아니라 model-facing 자연어 계약이다. 이 점은 구현 계획에서 의도적으로 받아들인 잔여 한계이므로 별도 결함으로 세지 않았다. 향후 runtime이 지원한다면 mutating command에는 description wording과 독립적인 mechanical gate를 두는 것이 낫다.
