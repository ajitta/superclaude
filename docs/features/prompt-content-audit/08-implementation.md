# 08 — P0 구현

브랜치는 `fix/prompt-content-audit`이다. 근거가 된 분석은 [03-analysis.md](./03-analysis.md) §4 P0이다. 수정 대상 문장은 모두 원문 인용으로 재확인한 뒤 고쳤다.

## 적용 내역

| # | 파일 | 변경 | 근거 |
|---|---|---|---|
| 1 | `agents/security-engineer.md` gotchas | `sc-not-webapp`에 "when the target repo is superclaude itself" 조건을 붙이고 "그 밖의 저장소는 웹 취약점까지 전체 검토"를 명시했다. `false-positive`를 `sc-installer-writes`로 바꾸고 같은 조건을 붙였다 | 03d High: 조건 없는 "skip web-vuln scans"가 사용자 웹앱 감사에서 스캔 생략을 유도했고 :49 OWASP 체크리스트와 충돌했다 |
| 2 | `agents/backend-architect.md` gotchas | `content-not-service`, `cli-simplicity`에 같은 조건을 붙이고 "Other repos keep their own stack"을 추가했다. 전보체를 문장으로 고쳤다 | 03c Med, 03d High: 저장소 전용 내용 누수 |
| 3 | `agents/frontend-architect.md` gotchas | `no-frontend-on-sc`, `plain-cli-output`에 같은 조건을 붙였다 | 같음 |
| 4 | `agents/git-workflow.md:44` | "(Edit + Write disallowed)"를 사실대로 고쳤다. 도구 설정은 Edit/Write를 막지 않으며, agent가 git 작업에 머무르고 파일 변경은 사용자나 구현 agent에게 맡긴다고 썼다 | 03c High: 존재하지 않는 차단을 서술하고 있었다. `disallowedTools` 복구는 보류 (03-analysis §3) |
| 5 | `agents/self-review.md` gotchas | "'42/42 pass' requires running tests"를 다음으로 바꿨다: 테스트 출력이 손에 있어야 하고(호출자가 전달하거나 로그에 있음), 이 agent의 도구로는 테스트를 실행할 수 없으므로 출력이 없으면 tests 차원은 `UNVERIFIED` | 03d High: `tools`에 Bash가 없는데 실행을 요구했다 |
| 6 | `agents/project-initializer.md` 예시 | "onboard me" 예시를 "메뉴에 온보딩 프리셋을 미리 선택해 제시하고, 사용자 확인 후 실행"으로 바꿨다 | 03c High: 예시가 `<never>auto-execute without menu`를 위반했다 |
| 7 | `modes/MODE_Business_Panel.md` 예시 | 두 예시를 Synthesis-First 순서와 라우팅 표(Market entry = Porter + Kim, Debate; Communication = Doumont + Godin, Socratic)에 맞게 재작성했다 | 03b High ×2 |
| 8 | `modes/MODE_Verbalized_Sampling.md` `<output_format>` | `p=`/`confidence`와 라벨을 각 후보 본문 **뒤**의 닫는 줄로 옮겼다. 이유도 적었다: 먼저 쓴 확률이나 라벨이 본문을 그쪽으로 끌어간다 | 03b High: :21 "only AFTER the text exists"와 포맷이 모순됐다 |
| 9 | `skills/sc-author/references/quality.md` 예시 | Opus 5만 기본으로 검증한다고 한정했다. Opus 5.5는 "guide에 기본값 없음 → 실제 실행으로 판단", Sonnet 5.5는 구체적 검사로 교체 | 03f High: 같은 파일 :116 표와 모순됐다 |
| 10 | `core/PRINCIPLES.md:11` | Assumption-Surfacing에 R12의 가역성 분기를 넣었다: 가역적이면 해석을 밝히고 진행, 비가역·>3 files/services·보안/데이터/파괴적 작업이면 먼저 질문 | 03a High: 항상 로드되는 텍스트가 on-demand R12와 반대 기준을 제시했다 |

차이는 10 files, +16/−16이다. 추가된 문장은 조건절이나 사실 정정뿐이고 새 규칙은 없다.

## 보류한 항목

03-analysis §3을 본다. 요점은 다음 세 가지다.

- **`RULES.md:16`:** 원문이 이미 "rather than requesting a change"로 한정하고 있고, canary `problem-statement-not-request`가 이 행동을 보호한다. 관찰된 실패가 없다.
- **simplicity-guide의 Agent 위임:** `--agent` 메인 스레드 모드의 정식 패턴이다. 서브에이전트 모드에서 쓸 대체 경로(:55 "else reports it unverified")도 이미 있다.
- **git-workflow `disallowedTools` 복구:** `672055ce`에서 의도적으로 제거됐다. memory가 켜진 agent에서 Write/Edit를 deny하면 MEMORY.md 쓰기와 충돌하는지 확인되지 않았다.

## 검증

| 검사 | 결과 |
|---|---|
| `uv run pytest -q -x` | 3415 passed, 3 skipped |
| `uv run superclaude author-check src/superclaude/skills/sc-author/references/quality.md` | 0 errors, 0 warnings |
| `make lint` | All checks passed |
| 수정 대상 문장의 사본 여부 (`git ls-files` 전체 grep) | src 내 사본 없음. `docs/archive/specs/`의 과거 설계 문서 1건에만 옛 VS 포맷이 남아 있고, 이는 아카이브라서 수정하지 않음 |

## 남은 일

- **canary 미실행:** core(`PRINCIPLES.md`)가 바뀌었으므로 `make release` 전에 `make canary-gates`를 돌리고 보고서를 확인해야 한다.
- **행동 변화 미측정:** 이번 수정은 정적 감사에 근거했다. 저장소의 `content-quality.md` Improvement Workflow는 관찰된 실패를 우선한다. 그래서 P0 범위를 "규칙과 직접 모순되는 예시·서술의 정정"과 "배포 누수의 조건화"로 한정했다. 행동 변화는 측정하지 않았다.
- **P1·P2:** 03-analysis §4에 남아 있다.
