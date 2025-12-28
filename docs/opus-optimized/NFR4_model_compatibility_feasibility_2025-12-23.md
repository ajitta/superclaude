# NFR4 Model Compatibility Feasibility Study

## SuperClaude v5.1 - Opus/Sonnet/Haiku 4.5 Support

| Item | Value |
|------|-------|
| **Date** | 2025-12-23 |
| **Research Depth** | --ultrathink (exhaustive) |
| **Confidence Level** | High (0.85) |
| **Recommendation** | FEASIBLE with modifications |

---

## 1. Executive Summary

NFR4 요구사항(Opus/Sonnet/Haiku 4.5 지원)은 **구현 가능**합니다. 세 모델이 핵심 기능을 공유하기 때문에 모델 불가지론적(model-agnostic) 접근 방식이 가장 효과적입니다.

### Key Findings

| Finding | Impact | Confidence |
|---------|--------|------------|
| 모델 자체는 자신의 정체성을 안정적으로 인식하지 못함 | Runtime detection 불가 | 0.95 |
| 세 모델 모두 200K 컨텍스트, 64K 출력, Extended Thinking 공유 | 통합 설정 가능 | 1.0 |
| effort 파라미터는 API 전용 (Claude Code에서 미사용) | Opus 전용 기능 제한적 | 1.0 |
| Claude Code 환경변수로 모델 설정 가능 | 배포 시 분기 가능 | 0.9 |

---

## 2. Claude 4.5 Model Family Specifications

### 2.1 Shared Capabilities (All Models)

| Capability | Opus 4.5 | Sonnet 4.5 | Haiku 4.5 |
|------------|----------|------------|-----------|
| Context Window | 200K | 200K (1M beta) | 200K |
| Max Output Tokens | 64K | 64K | 64K |
| Extended Thinking | ✅ | ✅ | ✅ |
| Context Awareness | ✅ | ✅ | ✅ |
| Tool Use | ✅ | ✅ | ✅ |
| Vision (Image Input) | ✅ | ✅ | ✅ |
| Prompt Caching | ✅ | ✅ | ✅ |

### 2.2 Model-Specific Differences

| Feature | Opus 4.5 | Sonnet 4.5 | Haiku 4.5 |
|---------|----------|------------|-----------|
| **Pricing (Input/Output per MTok)** | $5/$25 | $3/$15 | $1/$5 |
| **Cost Ratio** | 5x | 3x | 1x (baseline) |
| **Reasoning Depth** | Maximum | High | Near-Sonnet |
| **Speed** | Moderate | Balanced | Fastest |
| **Effort Parameter** | ✅ (API only) | ❌ | ❌ |
| **Best Use Case** | Complex reasoning, Architecture | Most tasks, Coding | High-volume, Real-time |
| **Knowledge Cutoff** | March 2025 | January 2025 | February 2025 |

### 2.3 Key Research Sources

1. **Anthropic Official Docs**: platform.claude.com/docs
2. **Claude Pricing Page**: anthropic.com/claude pricing
3. **Introspection Research**: transformer-circuits.pub/2025/introspection
4. **Claude Code Model Config**: code.claude.com/docs/en/model-config

---

## 3. Runtime Model Detection Analysis

### 3.1 Critical Finding: Models Cannot Reliably Self-Identify

Anthropic의 2025년 introspection 연구에 따르면:
- Claude Opus 4/4.1도 자기 모델 식별 성공률이 **~20%**에 불과
- Extended thinking 활성화 시에도 신뢰할 수 있는 자기 인식 불가
- 시스템 프롬프트에서 모델 정체성을 주입하는 것이 유일한 안정적 방법

### 3.2 Claude Code Model Configuration

Claude Code에서 모델 설정 방법:

```bash
# Environment Variables
export ANTHROPIC_MODEL="claude-opus-4-5-20251101"
export ANTHROPIC_DEFAULT_OPUS_MODEL="claude-opus-4-5-20251101"
export ANTHROPIC_DEFAULT_SONNET_MODEL="claude-sonnet-4-5-20250929"
export ANTHROPIC_DEFAULT_HAIKU_MODEL="claude-haiku-4-5"

# Mid-session switching
/model opus
/model sonnet
/model haiku

# Startup flag
claude --model claude-sonnet-4-5-20250929
```

### 3.3 Limitation

환경변수는 LLM 런타임 컨텍스트에 직접 노출되지 않음. 모델이 자신의 정체성을 알기 위해서는 **외부에서 주입**해야 함.

---

## 4. Implementation Options Analysis

### Option A: Static Multi-Profile (Deployment-time)

**개념**: 모델별 별도 프로파일 파일 생성, 배포 시 선택

```
src/core/
├── OPUS_PROFILE.md
├── SONNET_PROFILE.md
└── HAIKU_PROFILE.md
```

| Criterion | Score |
|-----------|-------|
| Feasibility | High |
| Complexity | Low (3-4h) |
| Maintenance | Medium (3 files) |
| User Experience | Acceptable |

**Deploy Script 예시**:
```bash
./deploy.sh --model sonnet  # SONNET_PROFILE.md → ~/.claude/
```

### Option B: Model-Agnostic Universal (RECOMMENDED)

**개념**: 모델 특정 참조 제거, 공통 기능 기반 단일 설정

| Criterion | Score |
|-----------|-------|
| Feasibility | **Highest** |
| Complexity | Low-Medium (2-4h) |
| Maintenance | **Low** (single source) |
| User Experience | **Seamless** |

**변경 사항**:
1. `OPUS_PROFILE.md` → `MODEL_PROFILE.md`
2. `<config model="opus-4.5">` → `<config model="claude-4.5">`
3. "Core Rules (Opus 4.5)" → "Core Rules (Claude 4.5)"
4. effort 파라미터 참조를 "API-only" 주석으로 변경

### Option C: User-Declared Model Identity

**개념**: 세션 시작 시 사용자가 모델 선언

```
/sc:load --model opus
```

| Criterion | Score |
|-----------|-------|
| Feasibility | Medium |
| Complexity | Medium |
| User Experience | Added friction |

### Option D: Capability-Based Adaptive (NOT RECOMMENDED)

**개념**: 런타임에 기능 감지로 모델 추론

| Criterion | Score |
|-----------|-------|
| Feasibility | **Low** |
| Complexity | High |
| Reliability | Poor |

---

## 5. Recommended Implementation Strategy

### 5.1 Primary Approach: Model-Agnostic Core (Option B)

**Phase 1: Core Changes (2h)**

| File | Change |
|------|--------|
| `src/CLAUDE.md` | `<config model="claude">` |
| `src/core/OPUS_PROFILE.md` | Rename → `MODEL_PROFILE.md`, generalize content |
| `src/core/RULES_CORE.md` | "Core Rules (Claude 4.5)" |

**Phase 2: Documentation (1h)**

- README에 모델 호환성 섹션 추가
- 모델별 비용 고려사항 문서화
- Opus 전용 기능 (effort parameter) 명시

**Phase 3: Testing (2h)**

각 모델에서 테스트:
- [ ] Core rules 동작
- [ ] Mode activation (deep-research, brainstorming, etc.)
- [ ] MCP integration (Serena, Tavily, Sequential, etc.)
- [ ] Agent invocation (/sc:agent)
- [ ] Commands (/sc:research, /sc:analyze, etc.)

### 5.2 Token Budget Strategy

모든 모델이 동일한 컨텍스트 윈도우를 공유하므로, 토큰 전략은 **비용 최적화** 중심:

| Model | Recommended Default | Thinking Depth | --uc Mode |
|-------|---------------------|----------------|-----------|
| Haiku 4.5 | --uc enabled | --think max | Default on |
| Sonnet 4.5 | Standard | Full range | Optional |
| Opus 4.5 | Full capability | --ultrathink | Optional |

**PRD 요구사항 준수**:
- NFR1: RULES_CORE.md < 800 tokens ✅ (현재 ~150)
- FR3: Context compression at 70% ✅

---

## 6. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Opus 전용 기능 손실 | Low | Low | effort parameter는 이미 API-only로 제외됨 |
| 모델별 성능 차이 | Medium | Medium | 문서화로 사용자 기대치 관리 |
| Breaking changes | Low | Low | 파일명 변경만, 기능 동일 |
| 테스트 미흡 | Medium | High | Phase 3 테스트 필수 |

---

## 7. Implementation Effort Estimate

| Phase | Tasks | Effort |
|-------|-------|--------|
| Phase 1 | Core file changes | 2h |
| Phase 2 | Documentation | 1h |
| Phase 3 | Testing (3 models) | 2h |
| Phase 4 | Bug fixes | 1h |
| **Total** | | **6h** |

---

## 8. Conclusion

### Verdict: NFR4 IS FEASIBLE

**Model-Agnostic 접근 방식**이 가장 실용적:

1. 세 모델이 핵심 기능(Extended Thinking, Context Awareness, Tool Use)을 공유
2. 런타임 모델 감지가 불가능하므로 통합 설정이 최선
3. effort 파라미터는 API 전용이므로 Claude Code에서 영향 없음
4. 구현 복잡도 낮음 (4-6시간)
5. Breaking changes 최소화

### Next Steps

1. `OPUS_PROFILE.md` → `MODEL_PROFILE.md` 리팩터링
2. 모델 특정 참조 제거 (CLAUDE.md, RULES_CORE.md)
3. 각 모델에서 통합 테스트 수행
4. README에 호환성 문서 추가

---

## Sources

1. [Anthropic Claude Models Overview](https://platform.claude.com/docs/en/about-claude/models/overview)
2. [What's New in Claude 4.5](https://platform.claude.com/docs/en/about-claude/models/whats-new-claude-4-5)
3. [Claude Code Model Configuration](https://code.claude.com/docs/en/model-config)
4. [Emergent Introspective Awareness in LLMs](https://transformer-circuits.pub/2025/introspection)
5. [Claude Opus 4.5 Announcement](https://www.anthropic.com/claude/opus)
6. [Claude Sonnet 4.5 System Card](https://www.anthropic.com/claude-sonnet-4-5-system-card)
7. [Claude Pricing](https://www.anthropic.com/pricing)
8. [Claude Code Environment Variables](https://gist.github.com/unkn0wncode/f87295d055dd0f0e8082358a0b5cc467)

---

*Generated by SuperClaude v5 - /sc:research --ultrathink*
*Date: 2025-12-23*
