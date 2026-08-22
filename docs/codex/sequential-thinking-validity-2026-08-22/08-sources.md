---
status: complete
retrieved_at: 2026-08-22
---

# 출처 목록

## 1차 자료 — 모델

- [Prompting Claude Opus 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5) — Opus 5의 과검증, verbosity, tool behavior.
- [What's new in Claude Opus 5](https://platform.claude.com/docs/en/about-claude/models/whats-new-opus-5) — thinking 기본 on, effort, 모델 기능.
- [Prompting Claude Fable 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5) — 과처방 skill, reasoning extraction, long-run scaffolding.
- [Introducing Claude Fable 5 and Claude Mythos 5](https://platform.claude.com/docs/en/about-claude/models/introducing-claude-fable-5-and-claude-mythos-5) — adaptive thinking 항상 on, raw CoT 비공개.
- [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices) — adaptive thinking과 일반 지침 우선.
- [Thinking](https://platform.claude.com/docs/en/about-claude/models/extended-thinking-models) — interleaved thinking, 비용, tool-use 상호작용.
- [The “think” tool](https://www.anthropic.com/engineering/claude-think-tool) — 2025 실험과 2025-12-15 native thinking 우선 업데이트.
- [How tool use works](https://platform.claude.com/docs/en/agents-and-tools/tool-use/how-tool-use-works) — client tool round trip과 컨텍스트 계약.

## 1차 자료 — Sequential MCP

- [npm package](https://www.npmjs.com/package/@modelcontextprotocol/server-sequential-thinking) — 공식 package 페이지.
- [npm latest metadata](https://registry.npmjs.org/@modelcontextprotocol%2Fserver-sequential-thinking/latest) — 최신 버전과 tarball.
- [업스트림 README](https://github.com/modelcontextprotocol/servers/blob/main/src/sequentialthinking/README.md) — 기능·설정·`DISABLE_THOUGHT_LOGGING`.
- [업스트림 tool schema](https://github.com/modelcontextprotocol/servers/blob/main/src/sequentialthinking/index.ts) — description, input/output schema.
- [serverInfo 버전 불일치 #4575](https://github.com/modelcontextprotocol/servers/issues/4575) — `2026.7.4` 배포판의 `0.2.0` 보고 버그.
- [MCP security policy](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/SECURITY.md) — local stdio 서버의 신뢰·권한 경계.

## 유지보수·사용성 보조 자료

- [branch/revision 활용 부족 이슈 #2332](https://github.com/modelcontextprotocol/servers/issues/2332) — 낮은 등급의 로그 기반 관찰.
- [hardening draft PR #3324](https://github.com/modelcontextprotocol/servers/pull/3324) — 현 배포 기능이 아닌 미병합 draft.

## 커뮤니티·사례 자료

- [r/mcp — Is Sequential Thinking MCP still a thing?](https://www.reddit.com/r/mcp/comments/1qritks/is_sequential_thinking_mcp_still_a_thing/) — 2026 회의적 평가.
- [r/OpenaiCodex — still using Sequential Thinking?](https://www.reddit.com/r/OpenaiCodex/comments/1vk25xb/are_you_guys_still_using_the_sequential_thinking/) — 2026-08 토큰·A/B 경험담.
- [r/AugmentCodeAI — Better results without Sequential Thinking?](https://www.reddit.com/r/AugmentCodeAI/comments/1neojmj/better_results_without_sequential_thinking_mcp/) — 긍정 경험담.
- [r/mcp — 4 MCPs I use daily](https://www.reddit.com/r/mcp/comments/1kpgrft/4_mcps_i_use_daily_as_a_web_developer/) — 계획 대화 사용 사례.
- [58K LoC Rust migration 사례](https://dev.to/kirodotdev/taming-large-codebases-with-kiro-lessons-from-a-58k-loc-rust-migration-36p9) — 비통제 성공 사례.
- [ClaudeLog Sequential Thinking MCP](https://claudelog.com/claude-code-mcps/sequential-thinking-mcp/) — native reasoning과의 중복·비용에 대한 2차 설명.

## 저장소 내부 근거

- `src/superclaude/mcp/MCP_Sequential.md:1-40`
- `src/superclaude/core/FLAGS.md:17-38`
- `src/superclaude/scripts/context_loader.py:138,254-258,597-628`
- `src/superclaude/cli/install_mcp.py:33-42,482-500`
- `src/superclaude/mcp/README.md:5-17,41-49`
- `README.md:207-215,564-618`
- `docs/guides/2026-03-22-context-engineering-guide-ko.md:25-53,272-280`
- `docs/features/opus5-fable5-alignment/02-research.md:22-42,125-133,158-172,192-214,238-252`
- `docs/features/opus5-fable5-alignment/README.md:77-93`

## 인용 주의

커뮤니티 자료는 효능을 확정하는 출처가 아니다. Anthropic `think` 도구 결과도 Claude 3.7과 다른 schema의 실험이므로 Sequential MCP의 Opus 5/Fable 5 성능 수치로 인용하면 안 된다.

