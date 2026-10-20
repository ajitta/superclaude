**superclaude의 가장 큰 약점은 절차가 촘촘한 데 비해, 그 절차가 실제로 지켜졌는지 확인하는 장치는 제한적이라는 점입니다.** 앞서 읽은 `stable` 소스 기준이며, 실사용 실패율이나 성능을 측정한 평가는 아닙니다.

### 1. ‘강한 지시’가 ‘실행 보장’처럼 보일 수 있습니다

명령에는 `hard gate`, `mandatory`, `never` 같은 표현이 있지만, 대부분 모델이 읽고 따르는 지시문입니다. 아키텍처 문서가 기계적 강제로 구분한 것은 파일 크기·파괴적 명령·반복 실패 가드입니다.

따라서 명세 검토나 승인 단계를 건너뛰어도, 이를 항상 실행 단계에서 차단하는 것은 아닙니다. **사용자가 절차의 강도를 실제 보장 수준보다 높게 받아들일 위험**이 있습니다.  
근거: [아키텍처의 Enforcement Boundary](https://github.com/ajitta/superclaude/blob/stable/src/superclaude/ARCHITECTURE.md).

### 2. 각 명령은 상세하지만, 명령 사이의 계약은 덜 정리돼 있습니다

확인한 예는 다음과 같습니다.

- `implement`가 기능을 `complete`로 표시한 뒤 `test`와 `reflect`가 남을 수 있습니다.
- 대형 작업의 대표 흐름에는 명세 리뷰가 있지만 구현 후 코드 리뷰는 빠져 있습니다.
- 계획 경유 구현과 직접 구현에서 TDD 요구가 동일하게 명시되지 않습니다.

문제는 명령 하나의 설명 부족보다 **상태·입력·출력·다음 단계의 조건이 서로 완전히 맞물리지 않는 것**입니다. 사용자가 명령을 잘 조합해야 흐름이 완성됩니다.  
근거: [README](https://github.com/ajitta/superclaude/blob/stable/README.md), [implement](https://github.com/ajitta/superclaude/blob/stable/src/superclaude/commands/implement.md), [test](https://github.com/ajitta/superclaude/blob/stable/src/superclaude/commands/test.md).

### 3. 같은 모델의 해석이 문서를 거치며 강화될 수 있습니다

의도 → 탐색 → 설계 → 계획 → 구현이 연결되는 것은 장점입니다. 하지만 초기에 잘못 해석하면 후속 단계가 그 해석을 일관되게 구체화할 수도 있습니다.

원문 보존과 의도 대조, 독립 리뷰가 이를 줄이도록 설계돼 있습니다. 다만 기본 리뷰가 언제나 독립된 관점에서 수행되는 것은 아니며, 별도 리뷰어를 쓰더라도 제공받는 자료에 같은 가정이 들어갈 수 있습니다.

**문서 간 일관성만으로 요구 해석의 정확성을 입증할 수는 없습니다.** 실제 사용 사례·반례·수용 테스트로 원래 문제에 되돌아가는 검사가 필요합니다.  
근거: [brainstorm](https://github.com/ajitta/superclaude/blob/stable/src/superclaude/commands/brainstorm.md), [review](https://github.com/ajitta/superclaude/blob/stable/src/superclaude/commands/review.md).

### 4. 절차를 운영하는 비용이 생깁니다

계획 체크박스, `Deviations`, 기능 README, 문서 상태, 리뷰 기록을 함께 관리해야 합니다. 이 기록들은 장기 작업에 유용하지만, 코드가 바뀔 때마다 동기화해야 하는 유지 비용도 만듭니다.

작은 작업을 위한 생략 규칙은 있습니다. 그러나 **언제 절차를 생략하고 언제 강화할지 판단하는 책임도 다시 모델에 돌아갑니다.** 과하게 적용하면 승인과 문서 작업이 늘고, 느슨하게 적용하면 핵심 검토가 빠질 수 있습니다.

### 5. 일부 판단 규칙이 의도를 거칠게 대리합니다

예를 들어 다음 기준이 있습니다.

- 영향 파일·단위 수로 승인 필요성을 판단
- 선택지 문자나 연속된 단어 일치로 사용자 결정의 `confirmed` 여부 분류
- 특정 플래그·키워드로 규칙과 모드 주입

구현하기 쉬운 기준이지만, 실제 위험이나 사용자의 명확한 동의를 정확히 나타내지는 못합니다. 한 파일의 권한 수정이 여러 파일의 이름 변경보다 위험할 수 있고, 한국어로 분명히 선택했어도 표현 일치 규칙이 놓칠 수 있습니다.

도메인별 예외가 일부 보완하지만, **표면적인 신호를 의미 판단과 혼동할 여지**는 남습니다.  
근거: [품질 규칙](https://github.com/ajitta/superclaude/blob/stable/src/superclaude/core/rules/RULES_QUALITY.md), [결정 분류 규칙](https://github.com/ajitta/superclaude/blob/stable/src/superclaude/commands/brainstorm.md).

### 6. 좋은 지침과 실제 효과 사이의 검증이 더 필요합니다

규칙이 구체적이고 서로 참조된다는 사실과, 그 규칙이 실제로 결함·재작업·의도 오해를 줄인다는 사실은 별개입니다.

이번에 읽은 자료만으로는 **프레임워크 전체가 기본 Claude Code보다 얼마나 개선되는지** 판단할 수 없습니다. 개별 평가 자료가 있더라도, 작업 종류·모델·컨텍스트가 달라지면 결과가 유지되는지 따로 봐야 합니다.

개선 우선순위를 정한다면 **① 완료 판정의 신뢰성 → ② 명령 간 계약 정리 → ③ 실제 작업으로 규칙의 효과와 비용 측정**입니다. 새 명령이나 규칙을 더 추가하는 것보다, 기존 절차 중 무엇이 오류를 줄이고 무엇이 부담만 늘리는지 확인하는 편이 먼저입니다.