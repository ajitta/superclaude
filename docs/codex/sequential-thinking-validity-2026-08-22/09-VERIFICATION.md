---
status: partial_model_efficacy_unmeasured
verified_at: 2026-08-22
repository_commit: d44a058a2d3a5950a157047778a3707c214599cd
---

# 검증 기록

## 완료한 검증

### npm 배포판

실행:

```bash
npm view @modelcontextprotocol/server-sequential-thinking \
  version time.modified repository.url dist.tarball --json
```

관찰:

```text
version: 2026.7.4
time.modified: 2026-07-04T23:05:13.436Z
repository: https://github.com/modelcontextprotocol/servers.git
```

`npm pack ...@latest`로 받은 tarball의 `package/package.json`도 `2026.7.4`였고, `dist/lib.js`는 `thoughtHistory`와 `branches`를 메모리에 저장한 뒤 메타데이터를 반환했다. 별도 모델·검색·검증 엔진 호출은 없었다.

### MCP 프로토콜 smoke test

최신 패키지에 `initialize`, `tools/list`, `tools/call`을 전송했다.

관찰:

- 초기화 성공.
- npm version과 달리 `serverInfo.version`은 `0.2.0`.
- `sequentialthinking` 한 도구만 노출.
- `thought: "Audit probe: no sensitive data."` 호출 성공.
- 응답은 `thoughtNumber`, `totalThoughts`, `nextThoughtNeeded`, `branches`, `thoughtHistoryLength`만 포함.
- 같은 thought 전문이 기본 stderr에 출력됨.
- 같은 입력을 두 번 호출하면 `thoughtHistoryLength`가 `1`에서 `2`로 증가함. 선언된 `idempotentHint: true`와 실제 동작이 불일치.
- `DISABLE_THOUGHT_LOGGING=true`로 두 번째 probe를 실행했을 때 thought 전문 stderr 출력은 사라졌지만 state 누적은 그대로였음.

이는 업스트림 이슈 #4575와 일치한다.

### SuperClaude 연결 추적

정적 추적으로 확인한 호출 경계:

```text
사용자 --seq
  -> context_loader TRIGGER_MAP
  -> MCP_Sequential.md 선택
  -> 기본 Tier 0 한 줄 hint 주입
```

이 경로에는 `claude mcp add`, MCP 프로세스 start/stop, tool allow/deny가 없다. 실제 등록은 별도의 `superclaude mcp` 설치 경로다.

### 공식 모델 지침

2026-08-22에 Opus 5·Fable 5·prompting best practices·thinking 문서를 열어 다음을 교차확인했다.

- Opus 5: thinking 기본 on, effort로 깊이 조절.
- Fable 5: adaptive thinking 항상 on, raw CoT 미반환.
- adaptive thinking 모델: 도구 호출 사이 thinking 자동 지원.
- Opus 5: 과도한 검증 지시는 비용 증가 가능.
- Fable 5: 구형 과처방 skill은 품질 저하 가능, reasoning 재현 지시에는 거부 위험.
- Anthropic `think` 글: 2025-12-15 이후 대부분의 경우 native thinking 우선.

## 검증하지 못한 핵심 항목

Opus 5와 Fable 5에서 Sequential MCP의 **정확한 품질 효과 크기**는 검증되지 않았다. 공개 직접 benchmark를 찾지 못했고, 이 조사에서 유료 반복 A/B도 실행하지 않았다.

따라서 다음 표현만 증거에 맞는다.

- 맞음: “최신 두 모델에서 기본 사용을 정당화할 증거가 없다.”
- 맞음: “공식 방향과 구현 구조는 native thinking 우선을 지지한다.”
- 과장: “Sequential MCP가 Opus 5/Fable 5에서 항상 성능을 떨어뜨린다.”
- 과장: “Fable 5에서 이 MCP가 반드시 reasoning extraction 거부를 일으킨다.”

## 문서 검증 결과

문서 생성 후 다음을 실행했다.

```bash
git diff --check
rg -n 'turn[0-9]+(search|view|reddit)' \
  docs/codex/sequential-thinking-validity-2026-08-22
rg -n '30-50% fewer|2025\.12\.18|2026\.7\.4|default off' \
  docs/codex/sequential-thinking-validity-2026-08-22
```

첫 번째는 Markdown whitespace 오류, 두 번째는 내부 검색 참조 ID 누출, 세 번째는 핵심 상충 주장과 판정이 문서에 남았는지 확인한다.

결과:

- `git diff --check`: 출력 없음. 새 문서는 untracked이므로 아래 전용 검사도 별도 실행.
- 내부 검색 참조 ID: 0건.
- Markdown 파일: 10개.
- trailing whitespace: 0건.
- YAML frontmatter parse 오류: 0건.
- `./` 상대 링크 누락: 0건.
- 버전 불일치, 무근거 토큰 절감 주장, 기본 off 판정이 관련 문서에 존재함을 확인.

Markdown 문서만 추가했으므로 Python test baseline에는 실행 위험이 없다. 소스 변경은 하지 않았다.
