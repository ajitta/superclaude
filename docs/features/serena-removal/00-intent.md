---
status: approved-for-plan
revised: 2026-10-12
---

# Intent: serena 사용, 참조, 의존성을 가진 부분들을 찾아서 제거

Author: ajitta.

## Problem
"문제를 일으킴". Serena가 일으키는 문제가 구체적으로 무엇인지는 not stated.

## Proposed outcome
"serena 사용, 참조, 의존성을 가진 부분들을 찾아서 제거하고 싶다"
"superclaude가 serena를 이용하고 참조하면서 동작하는 것을 없애려는 거야"

## Affected users and systems
- "배포 콘텐츠"
- "CLI/설치 코드"
- "레포 개발 환경"

범위 밖: 로컬 환경(~/.claude 설정, 등록된 Serena MCP 서버, auto memory)은 선택하지 않음.

## Constraints
- "쓰는 것을 막지는 않아". 사용자가 Serena를 쓰는 것을 막는 건 범위 밖.
- "기존 사용자 호환"
- ".serena 메모리 보존"

## Open questions
- Serena가 어떤 문제를 일으키는지 (증상, 발생 위치).
- ".serena 메모리 보존"이 레포에 남겨두는 것인지, 다른 곳으로 옮기는 것인지.
- "기존 사용자 호환"이 무엇을 지켜야 한다는 뜻인지 (예: 이미 Serena MCP를 등록한 사용자의 업그레이드).
