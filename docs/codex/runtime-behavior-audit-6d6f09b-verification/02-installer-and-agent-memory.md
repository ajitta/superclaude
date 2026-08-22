# Installer and agent memory

## P1 — 취소 또는 부분 입력이 user-scope 설치로 전환된다

관련 코드: `src/superclaude/cli/main.py:113-141`

bare `superclaude install`은 wizard를 실행하고, `click.Abort`를 잡으면 “입력 장치가 없음”으로 간주해 기본값인 user scope 설치를 계속한다. 문제는 Click이 EOF뿐 아니라 `KeyboardInterrupt`도 `Abort`로 변환한다는 점이다. 이는 [Click exception 문서](https://click.palletsprojects.com/en/stable/exceptions/)와 [Click `termui.py` 구현](https://github.com/pallets/click/blob/main/src/click/termui.py)에서 확인했다.

격리 재현:

1. bare `install` wizard에 `3`을 입력해 local scope를 고른다.
2. 다음 prompt에서 입력을 끝낸다(EOF).
3. 프로세스는 exit code 0으로 끝난다.
4. wizard 쪽 install 호출은 0회, fallback install은 1회다.
5. 실제 fallback 인자는 `scope="user"`, `base_path=~/.claude`다.

따라서 다음 두 불변조건이 깨진다.

- Ctrl-C는 취소여야 하지만 설치로 이어질 수 있다.
- 사용자가 이미 local/project를 골랐더라도 뒤 prompt의 EOF가 선택을 버리고 user scope로 바꾼다.

wizard가 앞 단계에서 `git init` 같은 작업을 수행한 뒤라면 그 부작용은 남은 상태에서 별도의 user 설치까지 일어날 수 있다.

권고:

- `click.Abort`를 “EOF 전용” 신호로 사용하지 않는다.
- unattended 여부는 wizard 진입 전에 결정하고, unattended 경로만 명시적으로 non-interactive 기본 설치로 보낸다.
- interactive prompt가 시작된 뒤의 `Abort`는 항상 비정상/취소 종료로 유지한다.
- 테스트에 bare stdin EOF, 첫 prompt 뒤 EOF, scope 선택 뒤 EOF, 각 단계 Ctrl-C를 모두 넣고 어떤 경우에도 fallback install이 호출되지 않음을 확인한다.

## P2 — agent memory 생성 실패가 성공으로 보고된다

관련 코드: `src/superclaude/cli/install_components.py:56-78`, `:468-470`

`ensure_agent_memory_dir()`는 `mkdir`의 `OSError`를 잡아 `None`을 반환한다. `install_all()`은 이 반환값을 검사하지 않고 component 설치를 계속한다.

재현에서는 target `.claude/agent-memory` 자리에 일반 파일을 먼저 만든 뒤 user-scope force install을 수행했다. 결과는 다음과 같았다.

- `install_all()` 성공값: `True`
- 설치 요약: failed 0
- `.claude/agent-memory`가 directory인가: `False`

agent frontmatter는 scope에 맞는 memory를 가리키도록 rewrite되지만 실제 store는 사용할 수 없다. 이 merge가 해결하려던 “agents declare a store that does not exist” 문제가 오류 경로에서는 침묵하는 성공으로 남는다.

권고:

- 지원 scope에서 memory directory를 만들지 못하면 설치 실패 수에 포함하고 최종 성공값을 `False`로 한다.
- 최소한 agent component 설치를 중단하고 실패 경로와 원인을 출력한다.
- permission denied, 같은 이름의 regular file, parent read-only를 테스트한다.

## P3 — local 설치를 project scope로 표시한다

관련 코드: `src/superclaude/scripts/session_init.py:35-42`

session status는 `claude_base()`가 home이면 `user`, 아니면 무조건 `project`로 표시한다. project와 local은 둘 다 `<project>/.claude`를 사용하므로 local 설치도 project scope로 출력된다.

이 표시는 실행 기능을 직접 깨지는 않지만, `settings.json`과 `settings.local.json`, `agent-memory`와 `agent-memory-local`을 구분해 장애를 조사할 때 잘못된 방향을 제시한다.

권고: 설치 marker 또는 실제 settings/agent-memory target을 기준으로 `user | project | local`을 판별한다. 두 scoped 설치가 공존할 수 있다면 우선순위와 ambiguous 상태도 명시한다.

## 정상 확인

- 입력이 끝까지 제공된 정상 wizard 경로는 선택한 scope와 force 값을 install에 전달한다.
- 사용자가 마지막 확인에서 명시적으로 `n`을 고르면 설치하지 않고 종료한다.
- 정상 local install에서는 `agent-memory-local`을 만들고 local git-exclude에 해당 경로를 추가한다.

문제는 정상 경로보다 `Abort` 의미의 합성 및 filesystem failure 보고에 있다.
