# 프롬프트 작성 가이드라인

<principles>
최소 고신호 토큰 | 자연스러운 권위 | Chain of Draft | XML 경계용 | 모델 비가지론
</principles>

<token_efficiency>
목표: 가장 작은 고신호 토큰 셋
기본값: 길수록 성능 저하
원칙: 핵심만, 중복 제거
</token_efficiency>

<tone>
자연스러운 권위: "Use X because Y"
피하기: "CRITICAL", "YOU MUST", "NEVER"
예시:
- ❌ "CRITICAL: You must never use markdown"
- ✅ "Response should be prose paragraphs for readability"
</tone>

<reasoning>
Chain of Draft: 계획 <5 단어/포인트
장황한 사고 텍스트는 중복/비용 증가
예시:
- ❌ "First, I need to understand the context. Then I'll analyze..."
- ✅ "Context → Requirements → Plan → Execute"
</reasoning>

<xml_structure>
XML은 경계 분리용 (Attention Interference 방지)
내용은 간결 우선
예시:
```xml
<instructions>Task definition</instructions>
<context>Background only</context>
```
</xml_structure>

<model_compatibility>
전제: 런타임에서 모델이 자기 정체성을 안정적으로 맞히지 못함
접근: 공통 기능 기반 단일 코어
4.5 패밀리 공통 코어 기준
모델별 특화 지시 지양
</model_compatibility>

<patterns>
지시: "Use X because Y"
계획: "Read → Analyze → Edit"
구조: XML로 섹션 분리, 내용 간결
검증: 짧은 체크리스트
</patterns>
