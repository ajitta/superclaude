# 03f — sc-author 스킬 감사

**대상:** `skills/sc-author/SKILL.md`와 `references/`의 8개 파일(agent.md, command.md, fields.yaml, format-xml.md, memory.md, output-style.md, quality.md, skill.md).

**전제:** sc-author는 `disable-model-invocation: true`라서 사용자가 직접 호출한다. 다른 사용자 프로젝트로 배포되어, 그들이 자기 agent/command/skill/output-style/memory 파일을 작성할 때 돕는다.

줄 번호는 감사 시점(커밋 `0c63688d`) 기준이다.

## 요약

- `superclaude author-check`로 SKILL.md와 reference 전부를 검사했다. 결과는 0 errors / 0 warnings다. SKILL.md가 가리키는 파일과 quality.md의 절 이름도 모두 실재한다.
- 지시가 절차형이고 강조어가 거의 없으며, 조건 대부분이 측정 가능하다. 현행 모델이 의도대로 따를 가능성이 높다.
- 확인된 결함은 두 가지다.
  - quality.md 안에서 Opus 5.5에 대한 서술이 모순된다.
  - 새 파일을 쓰기 전에 checker를 돌리라고 하는데, CLI는 파일이 이미 있어야만 실행된다.

## 발견사항

| 심각도 | path:line | 근거 인용 | 왜 문제인가 (모델 인식 관점) | 제안 | 상태 |
|---|---|---|---|---|---|
| High | quality.md:75-76 vs :116 | "Opus 5 and Opus 5.5 already verify" / 표 opus-5-5: "not stated as a default" | 예시가 표와 반대다. 모델은 예시를 더 강하게 모방하므로, Opus 5.5용 문서에서 검증 지시를 잘못 삭제하자고 제안한다 | 예시에서 Opus 5.5를 빼고 Opus 5로만 한정 | 재확인, **P0 적용** |
| High | SKILL.md:33, 35, 39 | "run step 6 early for them" / "Write only after the person approves" | 승인 전에는 새 파일이 디스크에 없다. 그런데 CLI는 `click.Path(exists=True)`(`cli/main.py:576`)라서 실행되지 않는다. 모델은 실패를 보고 즉석 우회책(임의로 파일 쓰기)을 만들거나 검사를 건너뛴다 | "새 문서는 scratch 경로에 초안을 저장해 검사"처럼 명시 | 재확인, P1 |
| Med | SKILL.md:15, 27; agent.md:14 | "do not shape this document"; "Sections… come from the type's reference" | 사용자 프로젝트에 이미 있는 작성 규칙과 섹션 관례를 형식·언어 외에는 따르지 말라는 정책이다. superclaude 내부 결정(D22)이 보편 규칙처럼 배포되어 사용자 의도와 충돌할 수 있다 | 충돌 시 사용자에게 묻도록 바꾸거나 정책의 이유를 명시 | P1 |
| Med | quality.md:61, 76, 114-119 | "candidate on Opus; on Sonnet, replace it…" | 작성 중인 문서를 나중에 어느 모델이 읽을지 알 수 없어서 모델별 판정을 실행할 수 없다. 날짜가 지나면 낡는 표라서 :38의 자체 규칙("expires with a date")과도 긴장 관계다 | 기본 판정은 "읽을 모델 중 가장 약한 쪽 기준으로 keep", 표는 참고용이라고 명시 | P1 |
| Med | quality.md:39 | "3 to 5, relevant and varied, each wrapped in `<example>`" | 응답 프롬프트용 조언을 지시 문서 전반의 보편 규칙으로 가르친다. 현행 모델은 예시를 과모방하고, CLAUDE.md와 skill이 비대해진다 | "출력 형식을 고정해야 할 때만" 같은 조건 추가 | P2 |
| Med | format-xml.md:19, 59-72 | "One root element" (CLAUDE.md 포함) | 루트 하나로 감싸는 것은 checker 편의일 뿐 모델 이해에는 이득이 없다. CLAUDE.md는 나중에 줄이 덧붙여지기 쉬워 X1 오류가 반복된다 | XML은 섞이는 콘텐츠(예시, 입력)를 구분할 때 권장하고, CLAUDE.md에는 루트를 강제하지 않기 | P2 |
| Med (확신도 낮음) | SKILL.md:46-47 | "`/doctor prompt-audit <path>`", "`claude plugin validate <skills directory>`" | 감사자가 아는 `/doctor`는 설치 진단 명령이라 이 하위명령의 실재를 확인할 수 없다. 없다면 존재하지 않는 명령을 안내하는 셈이 되어 quality.md:102의 Harm 기준에 걸린다 | 출처를 재확인하고 없으면 삭제 | P2 |
| Med (확신도 중) | memory.md:18 | "nest at most four hops" | 감사자의 기억으로는 import 최대 깊이가 5 hops다. 사실 오류일 수 있다 | 재확인 | P2 |
| Low (확신도 낮음) | memory.md:19 | "neither overrides the other" | 감사자의 기억으로는 project rule이 나중에 로드되어 우선한다. 충돌 판정의 근거가 달라진다 | 재확인 | P2 |
| Low | SKILL.md:19 | "for them alone (then the `~/.claude/` location)" | memory 유형에서 "나 혼자"가 이 프로젝트 전용(CLAUDE.local.md)인지 전역(~/.claude)인지 모호하다 | CLAUDE.local.md 분기 추가 | P2 |
| Low | fields.yaml:84-88 vs memory.md:19 | user-level rules 언급 | location 목록에 `~/.claude/rules/<name>.md`가 없다 | 목록에 추가 | P2 |
| Low | skill.md:45-46 | "may read … only partially"; "over 100 lines gets a table of contents" | 부분 읽기 우려는 구세대 harness·모델의 근거다. 규칙 자체는 해가 없지만 근거가 약하다 | 이유를 "탐색 비용"으로 교체 | P2 |
| Low | skill.md:38 | "shifting point of view hurts discovery" | 구세대 모델 근거다. 3인칭 권장 자체는 일관성 차원에서 해가 없다 | 이유 완화 | P2 |
| Low (확신도 낮음) | fields.yaml:55-56, 80, 41, 22-29 | `omitClaudeMd`, `experimental`, `force-for-plugin`, skill의 `shell`·`background`, `Artifact`·`ShareOnboardingGuide` 등 | 감사자 지식으로 확인할 수 없다. `tool_names`는 N2(error 등급) 판정 근거로 쓰이므로, 목록이 틀리면 사용자 문서에 오탐 오류가 난다 | 출처 날짜별로 재확인 | P2 |
| Low | SKILL.md:40-42 | "Fix F, R and X errors… An N finding…" | 코드 문자(F/R/X/N)의 뜻을 SKILL.md에서 설명하지 않는다. S1·S2 처리(경고로 보고)도 암묵적이다 | 한 줄 범례 추가 | P2 |

## 가르치는 가이드의 건전성

- **현행 모델에 맞는 부분:**
  - 강조어 완화(quality.md:34)와 규칙에 이유 붙이기(:31)
  - 문장 단위 no-op 판정과 "Enforced elsewhere"의 세 조건(:63)
  - Keep 목록: 되돌림 지시와 harness 특이사항을 보존한다.
  - 삭제할 때 근거를 적게 하는 형식
  - output style을 적용 범위 안으로 한정하라는 조언(output-style.md:36)
  - 서브에이전트에 `tools`를 지정하면 이름 없는 MCP 도구가 빠진다는 경고(agent.md:52)
- **구세대 관습이 남은 부분:** 예시 3~5개 의무, 부정형 대신 긍정형 지시(:32; 현행 모델은 부정 지시도 잘 따른다), 100줄을 넘으면 목차 필수, 3인칭 근거. 해롭지는 않지만 보편 규칙처럼 쓰여 있어 과적용될 위험이 있다.
- **XML 가이드:** "태그 이름에 특별한 의미가 없다"(:13)는 정확하다. 그러나 문서 전체를 루트 하나로 감싸는 형식을 선택지로 가르치는 것은 모델에게 이득 없이 유지보수 비용만 늘린다.

## 강점

- 단계마다 읽을 reference를 명시해 필요할 때만 로드한다. `${CLAUDE_SKILL_DIR}`로 경로를 해석하고, 승인 전에는 쓰지 않는다는 관문이 명확하다.
- 승인 메시지가 Resolve / Load set / Match 세 줄로 시작해서, 사람이 잘못된 경로나 빠진 문서를 잡을 수 있다.
- checker가 없으면 검사를 건너뛰되 실행하지 않은 검사를 했다고 주장하지 말라고 명시한다. 현행 모델의 과잉 보고를 억제한다.
- `allowed-tools`를 `Bash(superclaude author-check *)`로 좁혔다. 이 설정이 권한 프롬프트만 건너뛸 뿐 도구를 제한하지 않는다는 설명(skill.md:49)도 정확하다.
