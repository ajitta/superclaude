---
feature: plain-language-structure
phase: implementing
owner: ajitta
created: 2026-10-10
updated: 2026-10-10
related: ../../research/plain-language-output-style-chosh1179-2026-09-11.md
---

# Plain Language 스타일의 구조 손실과 만연체

Plain Language 출력 스타일(`src/superclaude/output-styles/plain-language.md`)을 켜면 표, 목록, 단계, 하위 단계로 써야 할 내용이 긴 문단으로 나오고 문장이 길어진다는 사용자 보고(2026-10-10)를 고친다. 정적 분석 결과 서식을 제한하는 문장이 허용하는 문장보다 많았고, 2026-09-11 A/B 측정(related 문서 §3)에서도 스타일 조건의 불릿 수가 기본 조건보다 적었다. 만연체 쪽은 아직 측정한 적이 없어 가설로 둔다.

## Documents

- [05-plan.md](./05-plan.md): Sonnet 5.5 기준선 측정, 구조 문구 교체, 조건부 문장 길이 문구 교체, 동기화 순서와 통과 기준
- [05a-plan-sentence-length.md](./05a-plan-sentence-length.md): Task 2 중단 뒤 문장 길이만 고치는 계획(05-plan Task 3을 옮김)
- [06-measurement.md](./06-measurement.md): 측정 환경, 측정 도구 변경, Sonnet 5.5 기준선과 시도별 판정 수치
