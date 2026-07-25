## 1. 콘텐츠 요약

이 영상의 핵심 주장은 **좋은 에이전트 스킬은 많은 지시문을 담는 문서가 아니라, 확률적인 AI가 매번 비슷한 작업 방식으로 움직이도록 만드는 최소한의 제어 장치**라는 것입니다. 영상은 Matt Pocock의 발표와 공개 스킬 저장소를 바탕으로 다음 네 가지 기준을 제시합니다. 

### ① 트리거: 누가 스킬을 호출하는가

스킬 호출 방식은 두 가지입니다.

* **사용자 호출**: 사용자가 슬래시 명령 등으로 직접 실행
* **모델 호출**: 모델이 스킬 설명을 보고 필요할 때 자동 실행

모델 호출은 편리하지만, 모든 스킬의 설명이 상시 컨텍스트에 들어가므로 토큰과 주의력을 소비합니다. 또한 모델이 적절한 순간에 스킬을 호출하지 않을 가능성도 있습니다.

반대로 사용자 호출은 예측 가능하지만, 어떤 스킬을 언제 사용할지 사람이 기억해야 합니다. 따라서 정답이 있는 문제가 아니라 **컨텍스트 부하를 모델이 부담할지, 인지 부하를 사용자가 부담할지 결정하는 트레이드오프**입니다.

### ② 구조: 절차와 참고자료를 분리하라

스킬의 내용은 크게 두 종류로 나뉩니다.

* **절차**: 에이전트가 따라야 할 작업 순서
* **참고자료**: 템플릿, 규칙, 예시, 도메인 정보

항상 필요한 절차는 `SKILL.md` 본문에 두되, 일부 상황에서만 필요한 자료는 별도 파일로 분리합니다. 본문에는 “필요한 경우 이 파일을 읽어라”라는 연결만 남깁니다.

이는 Anthropic 공식 문서가 설명하는 스킬 구조와도 일치합니다. Agent Skills는 `SKILL.md`와 선택적인 스크립트·참고자료를 묶은 패키지이며, 필요한 정보만 단계적으로 불러오는 방식으로 구성됩니다. ([Claude Platform][1])

### ③ 유도: 긴 설명보다 강한 용어를 사용하라

모델이 이미 학습한 소프트웨어 공학 용어에는 많은 행동 규칙이 압축되어 있습니다.

예를 들어 단순히 “작업을 작은 단위로 나눠라”고 장황하게 설명하는 대신 **vertical slice**라는 용어를 사용하면, 프론트엔드부터 백엔드까지 작동하는 작은 기능을 먼저 완성하는 개발 방식을 유도할 수 있습니다. Vertical Slice Architecture 역시 기능이나 요청 단위로 모든 계층의 관심사를 묶는 접근법으로 설명됩니다. ([Jimmy Bogard][2])

또 다른 기법은 **미래 단계 숨기기**입니다. 에이전트가 최종 목표를 미리 보면 중간 조사나 인터뷰를 서둘러 끝낼 수 있습니다. 그래서 다음과 같이 스킬을 분리합니다.

1. 요구사항을 질문하는 스킬
2. 답을 정리하는 스킬
3. 계획을 작성하는 스킬

질문 단계의 에이전트에게 “나중에 계획서를 작성한다”는 목표를 보여주지 않으면 현재 단계에 더 집중한다는 논리입니다.

### ④ 가지치기: 결과를 바꾸지 않는 문장은 삭제하라

영상이 권하는 가장 실용적인 방법은 **삭제 테스트**입니다.

> 문장을 지운 상태와 남긴 상태의 결과가 같다면, 그 문장은 필요하지 않다.

거대한 스킬에는 흔히 다음 문제가 쌓입니다.

* 같은 내용이 여러 곳에 있는 중복
* 과거 규칙이 그대로 남은 퇴적물
* 그럴듯하지만 모델 행동을 바꾸지 않는 무동작 문장

따라서 스킬을 계속 추가하기보다, 정기적으로 문장과 규칙을 삭제하며 결과 변화를 비교해야 합니다.

### Matt Pocock 저장소의 실제 구조

영상은 `mattpocock/skills` 저장소에서 이러한 원칙이 실제로 사용된다고 설명합니다.

특히 `grill-me`는 사용자에게 계획이나 설계를 집요하게 질문하는 인터뷰 흐름입니다. 현재 공개 저장소에서도 이 스킬은 사용자의 계획을 스트레스 테스트하고 의사결정의 각 분기를 해소하는 용도로 설명되어 있습니다. ([GitHub][3])

영상의 결론을 한 문장으로 압축하면 다음과 같습니다.

> **실패를 관찰하고, 검증된 공학 개념을 찾아, 모델이 이미 아는 강한 용어로 압축한 뒤, 최소한의 절차만 남기고 계속 삭제하라.**

---

## 2. 더 알아볼 자료와 링크

### 직접 관련 자료

* [현재 영상의 핵심 사례: Matt Pocock Skills 저장소](https://github.com/mattpocock/skills)
  실제 스킬의 디렉터리 구조, 설명문, 호출 관계를 확인할 수 있습니다. 저장소에는 `ask-matt`, `grill-with-docs`, 아키텍처 개선 및 이슈 분류 등 다양한 워크플로가 포함되어 있습니다. ([GitHub][3])

* [영상에서 언급한 원본 강연](https://www.youtube.com/watch?v=UNzCG3lw6O0)
  Matt Pocock의 “Building Great Agent Skills: The Missing Manual” 발표입니다.

* [grill-me 스킬 원문](https://github.com/mattpocock/skills/blob/main/skills/productivity/grill-me/SKILL.md)
  영상에서 강조한 “짧은 상위 호출 스킬”의 실제 형태를 확인하기 좋습니다. ([GitHub][4])

* [Anthropic 공식 Agent Skills 개요](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
  스킬의 파일 구조, 단계적 로딩, 스크립트와 리소스 구성 방식을 설명합니다. ([Claude Platform][1])

* [Anthropic 공식 Skills 예제 저장소](https://github.com/anthropics/skills)
  문서 제작, 테스트, 디자인, MCP 서버 생성 등 다양한 공식 예제를 직접 검토할 수 있습니다. ([GitHub][5])

### 영상의 개념을 이해하는 데 유용한 자료

* [Vertical Slice Architecture](https://www.jimmybogard.com/vertical-slice-architecture/)
  계층별로 시스템 전체를 먼저 만드는 대신, 하나의 요청이나 기능이 처음부터 끝까지 작동하도록 구현하는 방식입니다. ([Jimmy Bogard][2])

* [Martin Fowler: Keystone Interface](https://www.martinfowler.com/bliki/KeystoneInterface.html)
  작지만 완전히 작동하는 vertical slice를 빠르게 만드는 것이 왜 유용한지 설명합니다. ([martinfowler.com][6])

* [Agent Skills 관련 대규모 분석 연구](https://arxiv.org/abs/2602.08004)
  공개된 4만여 개의 스킬을 분석한 연구입니다. 스킬 생태계에 의도 수준의 중복이 많고, 안전성 및 품질 관리 문제가 존재한다고 보고합니다. 이는 영상의 “스킬을 더 추가하기보다 평가하고 가지치기해야 한다”는 주장과 연결됩니다. ([arXiv][7])

### 영상에서 바로 다시 볼 부분

* [트리거와 호출 방식](https://www.youtube.com/watch?v=YLq04CDeOTE&t=103s)
* [절차와 참고자료 분리](https://www.youtube.com/watch?v=YLq04CDeOTE&t=165s)
* [Vertical slice를 이용한 유도](https://www.youtube.com/watch?v=YLq04CDeOTE&t=205s)
* [미래 목표를 숨기는 기법](https://www.youtube.com/watch?v=YLq04CDeOTE&t=292s)
* [삭제 테스트](https://www.youtube.com/watch?v=YLq04CDeOTE&t=350s)
* [grill-me 사례 분석](https://www.youtube.com/watch?v=YLq04CDeOTE&t=403s)
* [최종 4단계 정리](https://www.youtube.com/watch?v=YLq04CDeOTE&t=496s)

---

## 3. 여기서 할 수 있는 유용한 작업

### 가장 실용적인 작업: 기존 스킬 감사

현재 사용 중인 `SKILL.md`, 커스텀 명령, 시스템 프롬프트를 다음 표로 검토할 수 있습니다.

| 점검 영역  | 확인 질문                                |
| ------ | ------------------------------------ |
| 트리거    | 반드시 자동 호출이어야 하는가, 사용자가 직접 호출해도 되는가?  |
| 설명문    | 모델이 정확히 언제 이 스킬을 선택해야 하는지 구분되는가?     |
| 구조     | 항상 필요한 절차와 가끔 필요한 참고자료가 분리됐는가?       |
| 용어     | 장황한 설명을 검증된 도메인 용어 하나로 압축할 수 있는가?    |
| 단계     | 최종 목표를 너무 일찍 보여줘 중간 단계를 서두르게 하지 않는가? |
| 중복     | 동일한 규칙의 정답 위치가 두 곳 이상 존재하지 않는가?      |
| 삭제 테스트 | 특정 문장을 제거했을 때 실제 결과가 달라지는가?          |

### 새로운 스킬을 만드는 최소 템플릿

```markdown
---
name: review-architecture
description: Use when the user wants to identify architectural risks in an existing codebase.
---

1. Inspect the repository structure and existing conventions.
2. Identify one thin vertical slice to analyze end to end.
3. Report evidence before recommending changes.
4. Read `references/smells.md` only when classifying architecture smells.
```

핵심은 길이가 아니라 다음 세 가지입니다.

* 호출 조건이 다른 스킬과 구별되는가
* 행동 순서가 관찰 가능한가
* 각 문장이 결과에 실질적인 영향을 주는가

### 작은 실험으로 효과 검증

같은 작업을 세 조건으로 실행해 비교할 수 있습니다.

1. 스킬 없이 실행
2. 기존 스킬로 실행
3. 가지치기한 스킬로 실행

비교 항목은 결과 품질뿐 아니라 다음을 포함해야 합니다.

* 스킬 호출 성공률
* 불필요한 질문 수
* 절차 누락 여부
* 토큰 사용량
* 결과의 일관성
* 사용자의 수정 횟수

### 용어집 만들기

프로젝트에 `CONTEXT.md` 또는 `GLOSSARY.md`를 만들어 다음을 정의할 수 있습니다.

```markdown
## Vertical slice
사용자가 실제로 실행할 수 있는 하나의 기능을 UI, API, 데이터 계층까지 완성한 단위.

## Done
코드 작성만 완료된 상태가 아니라 테스트, 검증, 문서화가 끝난 상태.

## Evidence-first review
개선안을 제시하기 전에 파일 경로, 코드 위치, 실행 결과를 먼저 제시하는 리뷰 방식.
```

이 방식은 여러 스킬에서 같은 개념을 반복 설명하는 문제를 줄이고, 팀과 에이전트가 동일한 용어를 사용하게 합니다.

### 추천 실행 순서

가장 효과적인 시작점은 새 스킬 설치가 아니라 다음 순서입니다.

1. 가장 자주 사용하는 스킬 하나를 선택
2. 사용자 호출과 모델 호출 중 어느 쪽이 적합한지 재검토
3. 본문에서 참고자료를 별도 파일로 이동
4. 핵심 행동을 표현하는 강한 도메인 용어 하나 추가
5. 문장을 하나씩 삭제하며 결과 비교
6. 실패 사례를 테스트 케이스로 기록

**판단:** 영상의 방법론은 스킬 작성뿐 아니라 `CLAUDE.md`, 프로젝트 규칙, 에이전트 워크플로, 반복 업무용 프롬프트를 정리할 때도 직접 적용할 수 있습니다. 다만 “짧을수록 무조건 좋다”가 아니라, **결과를 바꾸지 않는 내용은 짧든 길든 제거해야 한다**는 것이 더 정확한 해석입니다.

[1]: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview?utm_source=chatgpt.com "Agent Skills - Claude Platform Docs"
[2]: https://www.jimmybogard.com/vertical-slice-architecture/?utm_source=chatgpt.com "Vertical Slice Architecture"
[3]: https://github.com/mattpocock/skills?utm_source=chatgpt.com "mattpocock/skills: Skills for Real Engineers. Straight from ..."
[4]: https://github.com/mattpocock/skills/blob/main/skills/productivity/grill-me/SKILL.md?utm_source=chatgpt.com "skills/skills/productivity/grill-me/SKILL.md at main"
[5]: https://github.com/anthropics/skills?utm_source=chatgpt.com "anthropics/skills: Public repository for Agent Skills"
[6]: https://www.martinfowler.com/bliki/KeystoneInterface.html?utm_source=chatgpt.com "Keystone Interface"
[7]: https://arxiv.org/abs/2602.08004?utm_source=chatgpt.com "Agent Skills: A Data-Driven Analysis of Claude Skills for Extending Large Language Model Functionality"
