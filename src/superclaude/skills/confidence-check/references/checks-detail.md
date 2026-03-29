# Confidence Check — Detailed Check Definitions

## Check Weights

| Check | Weight | Tools | Validates |
|-------|--------|-------|-----------|
| No Duplicates | 25% | Grep, Glob, Serena | No existing similar functionality |
| Architecture | 25% | CLAUDE.md, pyproject.toml | Uses existing tech stack |
| Official Docs | 20% | Context7, WebFetch | Documentation reviewed |
| OSS Reference | 15% | Tavily, WebSearch | Working implementations found |
| Root Cause | 15% | Investigation | Problem source identified |

## MCP Integration

| MCP | Role | Fallback |
|-----|------|----------|
| Context7 | Official docs (Check 3) | WebFetch |
| Tavily | OSS search (Check 4) | WebSearch |
| Serena | Symbol detection (Check 1) | Grep/Glob |

## ROI

100-200 tokens check → saves 5,000-50,000 tokens (25-250x ROI)

## Hook

`validate_confidence_context.py` runs on PreToolUse for WebFetch/WebSearch — injects evidence-focus guidance (once per session).
