---
feature: plugin-install
phase: planning
owner: ajitta
created: 2026-10-05
updated: 2026-10-05
---

# clone 없이 설치: uv tool CLI + Claude Code plugin

지금 사용자가 SuperClaude를 설치하려면 저장소를 clone한 뒤 `make deploy`(editable 설치)를 실행해야 한다. 이 feature는 두 단계로 이 요구를 없앤다. 1단계에서는 Serena(`uv tool install -p 3.13 serena-agent`)처럼 한 줄로 CLI를 설치한다. 2단계에서는 같은 저장소를 Claude Code plugin marketplace로 만들어 `/plugin install`로 content와 hooks를 배포하고, hook 런타임은 1단계 CLI가 맡는다.

## Documents

- [05-plan.md](./05-plan.md): 1단계(README만 변경)와 2단계(plugin manifest, core 주입 hook, 검증, 4.21.0 릴리스) 구현 계획
