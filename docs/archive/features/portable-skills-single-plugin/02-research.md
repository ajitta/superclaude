---
status: complete
revised: 2026-10-08
---

# Research: 기존 설치를 깨지 않고 두 플러그인을 하나로 합치기

[00-intent.md](./00-intent.md)의 두 요구, "마켓플레이스도 하나의 플러그인으로"와 "Existing installs must not break"가 Claude Code에서 함께 성립하는지 로컬 probe로 확인했다. 결론: 마켓플레이스 항목만 지우면 기존 설치가 깨지고, `marketplace.json`에 `renames` 맵을 함께 넣으면 기존 사용자가 새 플러그인으로 자동 이전된다.

## Probe 환경

- Claude Code 2.1.292, 격리된 `CLAUDE_CONFIG_DIR`(사용자 `~/.claude`는 건드리지 않음).
- 마켓플레이스: 이름 `ajitta-socratic`인 scratch git 저장소. GitHub 사용자와 같은 경로(git clone 후 플러그인을 `plugins/cache/<marketplace>/<plugin>/<version>`에 복사)를 타도록 git으로 clone되게 했다. CC는 `git://`와 `file://` 마켓플레이스 소스를 거부하므로 `http://…/mkt.git`으로 등록하고 `GIT_CONFIG_*` 환경변수의 `insteadOf`로 로컬 저장소에 연결했다. 로컬 디렉터리로 등록하면 `readFromFolder`로 원본 폴더를 직접 읽어 GitHub 사용자와 동작이 달라지므로 쓰지 않았다.
- 버전:
  - v1: 지금 구조. `socratic-brainstorm` 3.2.1, `socratic-elenchus` 1.2.1 두 항목.
  - v2: `socratic` 1.0.0 한 항목. `plugins/socratic/skills/<skill>/`에 두 스킬. 이전 두 항목 삭제.
  - v3: v2 + `"renames": {"socratic-brainstorm": "socratic", "socratic-elenchus": "socratic"}`.

플러그인 이름 `socratic`은 probe용이다. 실제 이름은 아직 정하지 않았다.

## 결과

| 경우 | 절차 | 관찰 |
|---|---|---|
| A. 항목만 삭제 (v1→v2) | 두 플러그인 설치 → `claude plugin marketplace update` | 둘 다 `✘ failed to load`, `Plugin socratic-brainstorm not found in marketplace ajitta-socratic`. `claude plugin update`도 같은 이유로 실패. 캐시 파일은 남지만 로드되지 않음 |
| B. `renames` 추가 (v1→v3) | 두 플러그인 설치 → marketplace update → 세션 시작 | `enabledPlugins`의 이전 키 두 개가 `socratic@ajitta-socratic: true` 하나로 바뀜. 이전 설치는 `installed_plugins.json`에서 제거됨. 다음 세션 시작(`claude -p`, 로그인 확인 전 단계)에서 `socratic` 1.0.0이 자동 설치되고 `plugin list`는 `✔ enabled` |
| C. A 상태에서 새 플러그인도 설치한 사용자 → v3 | marketplace update → 세션 시작 | `enabledPlugins`가 `socratic@ajitta-socratic` 하나로 합쳐짐. 설치 목록도 `socratic` 하나뿐이라 같은 스킬이 두 번 로드되지 않음 |
| D. 두 스킬 구조 | `claude plugin validate` (플러그인, 마켓플레이스) → `claude plugin details` | 둘 다 `Validation passed`. `Skills (2)  socratic-brainstorm, socratic-elenchus`. 네임스페이스는 manifest 이름이라 슬래시 명령은 `/socratic:socratic-brainstorm` |

## 문서로 확인한 사실

출처: code.claude.com `plugins/host-marketplace`, `plugins/marketplace-reference` (2026-10-08 조회).

- `renames`는 이전 이름을 현재 이름이나 `null`에 매핑한다. 문서는 이 맵을 "append-only history"로 다루고, 모두 이전한 뒤에도 항목을 지우지 말라고 한다.
- 서드파티 마켓플레이스의 background auto-update는 기본으로 꺼져 있다. 업데이트를 하지 않는 사용자는 이전 clone을 계속 쓰므로 이전 플러그인이 그대로 동작한다.
- 마켓플레이스에는 deprecation 상태가 없다. 문서가 제시하는 대안은 항목 삭제 + `renames`의 `null` 매핑(+ 선택적으로 `forceRemoveDeletedPlugins`)이다.
- 문서에는 이름이 바뀐 플러그인이 `/plugin install`을 한 번 실행하기 전까지 `not cached`를 보고한다고 적혀 있지만, 2.1.292에서는 세션 시작 시 자동 설치됐다(경우 B).
- 알 수 없는 최상위 키는 무시된다. `renames`의 최소 지원 버전은 문서에 없다. `renames`를 모르는 CC 버전에서는 경우 A가 그대로 일어날 것으로 추정한다(미확인).

## 계획에 넘길 결론

1. Claude Code에서 "기존 설치가 깨지면 안 됨"은 `renames`로 지킬 수 있다. 이전 두 이름을 모두 새 이름에 매핑하는 것은 선택이 아니라 필수다. 없으면 경우 A가 된다.
2. 이전 후 동작 변화: 한쪽만 설치했던 사용자도 두 스킬을 모두 받는다. 플러그인 설치 사용자의 슬래시 명령이 `/socratic-brainstorm:socratic-brainstorm`에서 `/<새이름>:socratic-brainstorm`으로 바뀐다. 말로 부르는 호출은 바뀌지 않는다.
3. `package.py`의 생성 단계가 바뀐다. 원본 폴더의 `skills/` 금지 규칙은 그대로 두고, 생성되는 플러그인 폴더만 `skills/<skill>/` 구조가 된다. manifest 버전과 SKILL.md `metadata.version`이 같아야 한다는 지금 검사는 플러그인 하나에 스킬 둘인 구조에 맞는 규칙으로 바꿔야 한다.
4. `renames` 항목은 영구히 유지해야 하므로 테스트로 고정한다.

## 확인하지 못한 것

- claude.ai Customize › Plugins › Upload plugin이 두 스킬을 담은 zip을 받는지. 사용자가 직접 업로드해 확인해야 한다. 이미 업로드된 사본은 정적이라 저장소 변경에 영향을 받지 않는다.
- claude.ai의 Add marketplace 경로에서도 `renames`가 적용되는지.
- 로그인된 세션에서 스킬을 실제로 호출하는 단계. probe는 로더 수준(`plugin list`, `plugin details`, 설치 상태)까지만 확인했다.
- 실제 GitHub 전송. probe는 로컬 git clone을 썼고, clone 이후 경로는 같다고 가정했다.
- `renames`를 지원하는 최소 CC 버전.

## 사용자가 정할 것

- 새 플러그인 이름 (probe에서는 `socratic`)
- 버전 체계: 플러그인 버전 하나로 갈지, 스킬별 `metadata.version`을 어떻게 다룰지
- 이전 zip(`releases/socratic-brainstorm.zip`, `releases/socratic-elenchus.zip`)을 남길지. README와 Pages가 이 파일에 직접 링크한다
