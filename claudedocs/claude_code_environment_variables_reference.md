# Claude Code 환경 변수 완전 레퍼런스

**작성일**: 2026-01-28
**버전**: 1.0
**출처**: Anthropic 공식 문서, GitHub 소스 분석, 커뮤니티 가이드

---

## 목차

1. [빠른 시작](#1-빠른-시작)
2. [인증 및 API](#2-인증-및-api)
3. [모델 설정](#3-모델-설정)
4. [클라우드 제공자](#4-클라우드-제공자)
   - [AWS Bedrock](#41-aws-bedrock)
   - [Google Vertex AI](#42-google-vertex-ai)
   - [Microsoft Azure Foundry](#43-microsoft-azure-foundry)
   - [LLM 게이트웨이](#44-llm-게이트웨이)
5. [네트워크 및 프록시](#5-네트워크-및-프록시)
6. [TLS / mTLS 인증서](#6-tls--mtls-인증서)
7. [Bash / 셸 실행](#7-bash--셸-실행)
8. [컨텍스트 및 토큰 관리](#8-컨텍스트-및-토큰-관리)
9. [MCP 서버 설정](#9-mcp-서버-설정)
10. [프롬프트 캐싱](#10-프롬프트-캐싱)
11. [텔레메트리 및 개인정보](#11-텔레메트리-및-개인정보)
12. [OpenTelemetry (엔터프라이즈)](#12-opentelemetry-엔터프라이즈)
13. [UI 및 표시](#13-ui-및-표시)
14. [파일 및 경로](#14-파일-및-경로)
15. [업데이트 및 기능 제어](#15-업데이트-및-기능-제어)
16. [Hook 실행 컨텍스트 변수](#16-hook-실행-컨텍스트-변수)
17. [SuperClaude 프레임워크 전용](#17-superclaude-프레임워크-전용)
18. [설정 파일 우선순위](#18-설정-파일-우선순위)
19. [참고 문헌](#19-참고-문헌)

---

## 1. 빠른 시작

### 최소 설정 시나리오별

**개인 사용자 (Pro/Max 구독)**
```bash
# 로그인만으로 충분 — 환경 변수 불필요
claude login
```

**API 키 사용자**
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

**기업 프록시 환경**
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export HTTPS_PROXY="https://proxy.corp.com:8080"
export NODE_EXTRA_CA_CERTS="/path/to/corp-ca.pem"
```

**settings.json 방식 (Windows 권장)**
```json
{
  "env": {
    "ANTHROPIC_API_KEY": "sk-ant-...",
    "ANTHROPIC_MODEL": "claude-opus-4-5-20251101"
  }
}
```

> **참고**: 모든 환경 변수는 `settings.json`의 `"env"` 키로도 설정 가능합니다. Windows에서는 셸 `export`보다 이 방식이 안정적입니다.

---

## 2. 인증 및 API

| 변수 | 필수 | 기본값 | 용도 |
|------|------|--------|------|
| `ANTHROPIC_API_KEY` | Pro/Max 미구독시 필수 | None | API 키. `X-Api-Key` 헤더로 전송. [console.anthropic.com](https://console.anthropic.com)에서 발급 |
| `ANTHROPIC_AUTH_TOKEN` | 선택 | None | 커스텀 `Authorization: Bearer` 헤더. 3rd party 제공자 및 LLM 게이트웨이용. `apiKeyHelper`보다 우선 |
| `ANTHROPIC_CUSTOM_HEADERS` | 선택 | None | API 요청에 추가할 커스텀 HTTP 헤더. `Name: Value` 형식 (JSON) |
| `CLAUDE_CODE_API_KEY_HELPER_TTL_MS` | 선택 | None | `settings.json`의 `apiKeyHelper` 사용시 자격증명 갱신 주기 (밀리초) |
| `CLAUDE_CODE_OAUTH_TOKEN` | 선택 | None | OAuth 토큰. `claude setup-token`으로 설정. GitHub Action 등 CI/CD 환경용 |

---

## 3. 모델 설정

| 변수 | 기본값 | 용도 |
|------|--------|------|
| `ANTHROPIC_MODEL` | `claude-sonnet-4-5-20250929` | 기본 모델 오버라이드. 별칭 가능: `opus`, `sonnet`, `haiku`, `opusplan` |
| `ANTHROPIC_DEFAULT_OPUS_MODEL` | 최신 Opus | `opus` 별칭에 매핑되는 모델. Plan Mode에서 `opusplan` 계획 단계 |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | 최신 Sonnet | `sonnet` 별칭에 매핑되는 모델. `opusplan` 실행 단계 |
| `ANTHROPIC_DEFAULT_HAIKU_MODEL` | 최신 Haiku | `haiku` 별칭 및 백그라운드 작업용 모델 |
| `CLAUDE_CODE_SUBAGENT_MODEL` | None | Task 도구의 서브에이전트에 사용할 모델 |
| `CLAUDE_CODE_MAX_OUTPUT_TOKENS` | 32,000 | 요청당 최대 출력 토큰. 범위: 32,000 ~ 64,000 |
| `MAX_THINKING_TOKENS` | 31,999 | Extended Thinking 토큰 예산. `0`으로 비활성화 |
| ~~`ANTHROPIC_SMALL_FAST_MODEL`~~ | None | **Deprecated** — `ANTHROPIC_DEFAULT_HAIKU_MODEL` 사용 |
| ~~`ANTHROPIC_SMALL_FAST_MODEL_AWS_REGION`~~ | None | Bedrock Haiku 모델 리전. Deprecated |

---

## 4. 클라우드 제공자

### 4.1 AWS Bedrock

| 변수 | 필수 | 기본값 | 용도 |
|------|------|--------|------|
| `CLAUDE_CODE_USE_BEDROCK` | 조건부 | `0` | `1`로 설정하여 Bedrock 활성화 |
| `AWS_REGION` | Bedrock시 필수 | None | AWS 리전 (예: `us-east-1`) |
| `AWS_PROFILE` | 선택 | `default` | `.aws/` 자격증명 프로파일명 |
| `AWS_ACCESS_KEY_ID` | 조건부 | None | AWS 접근 키 |
| `AWS_SECRET_ACCESS_KEY` | 조건부 | None | AWS 비밀 키 |
| `AWS_SESSION_TOKEN` | 선택 | None | 임시 자격증명용 세션 토큰 |
| `AWS_BEARER_TOKEN_BEDROCK` | 선택 | None | Bedrock Bearer 토큰/API 키 |
| `AWS_DEFAULT_REGION` | 선택 | None | 기본 AWS 리전 (폴백) |
| `ANTHROPIC_BEDROCK_BASE_URL` | 선택 | None | 커스텀 Bedrock 엔드포인트 (LLM 게이트웨이용) |
| `CLAUDE_CODE_SKIP_BEDROCK_AUTH` | 선택 | `0` | `1`: AWS 인증 생략 (게이트웨이가 처리시) |

### 4.2 Google Vertex AI

| 변수 | 필수 | 기본값 | 용도 |
|------|------|--------|------|
| `CLAUDE_CODE_USE_VERTEX` | 조건부 | `0` | `1`로 설정하여 Vertex AI 활성화 |
| `CLOUD_ML_REGION` | Vertex시 필수 | None | GCP 리전 (예: `us-east5`, `global`) |
| `ANTHROPIC_VERTEX_PROJECT_ID` | Vertex시 필수 | None | Google Cloud 프로젝트 ID |
| `GCLOUD_PROJECT` | 선택 | None | 프로젝트 ID 오버라이드 (`ANTHROPIC_VERTEX_PROJECT_ID`보다 우선) |
| `GOOGLE_CLOUD_PROJECT` | 선택 | None | 대체 프로젝트 ID 오버라이드 |
| `GOOGLE_APPLICATION_CREDENTIALS` | 선택 | None | 서비스 계정 자격증명 JSON 파일 경로 |
| `CLAUDE_CODE_SKIP_VERTEX_AUTH` | 선택 | `0` | `1`: Google 인증 생략 (게이트웨이가 처리시) |
| `ANTHROPIC_VERTEX_BASE_URL` | 선택 | None | 커스텀 Vertex 엔드포인트 |
| `VERTEX_REGION_CLAUDE_3_5_HAIKU` | 선택 | None | Claude 3.5 Haiku Vertex 리전 오버라이드 |
| `VERTEX_REGION_CLAUDE_3_7_SONNET` | 선택 | None | Claude 3.7 Sonnet Vertex 리전 오버라이드 |
| `VERTEX_REGION_CLAUDE_4_0_OPUS` | 선택 | None | Claude 4.0 Opus Vertex 리전 오버라이드 |
| `VERTEX_REGION_CLAUDE_4_0_SONNET` | 선택 | None | Claude 4.0 Sonnet Vertex 리전 오버라이드 |
| `VERTEX_REGION_CLAUDE_4_1_OPUS` | 선택 | None | Claude 4.1 Opus Vertex 리전 오버라이드 |

### 4.3 Microsoft Azure Foundry

| 변수 | 필수 | 기본값 | 용도 |
|------|------|--------|------|
| `CLAUDE_CODE_USE_FOUNDRY` | 조건부 | `0` | `1`로 설정하여 Foundry 활성화 |
| `ANTHROPIC_FOUNDRY_RESOURCE` | Foundry시 필수 | None | Foundry 리소스명 (예: `my-resource`) |
| `ANTHROPIC_FOUNDRY_BASE_URL` | 선택 | None | Foundry 전체 엔드포인트 URL |
| `ANTHROPIC_FOUNDRY_API_KEY` | 선택 | None | Foundry API 키. Entra ID 사용시 생략 |
| `CLAUDE_CODE_SKIP_FOUNDRY_AUTH` | 선택 | `0` | `1`: Azure 인증 생략 |

### 4.4 LLM 게이트웨이

프록시/게이트웨이를 통해 API 요청을 라우팅할 때 사용합니다.

| 변수 | 용도 |
|------|------|
| `ANTHROPIC_BASE_URL` | Anthropic API 게이트웨이 (예: `https://litellm:4000`) |
| `ANTHROPIC_BEDROCK_BASE_URL` | Bedrock 게이트웨이 |
| `ANTHROPIC_VERTEX_BASE_URL` | Vertex 게이트웨이 |
| `ANTHROPIC_FOUNDRY_BASE_URL` | Foundry 게이트웨이 |
| `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS` | `1`: `anthropic-beta` 헤더 비활성화. 3rd party 제공자 게이트웨이에서 필요 |

---

## 5. 네트워크 및 프록시

| 변수 | 기본값 | 용도 |
|------|--------|------|
| `HTTPS_PROXY` | None | HTTPS 프록시 서버 (권장). 예: `https://proxy.example.com:8080` |
| `HTTP_PROXY` | None | HTTP 프록시 서버 (HTTPS 불가시 대체) |
| `NO_PROXY` | None | 프록시 바이패스 도메인/IP 목록 (공백 또는 쉼표 구분). `*`로 전체 바이패스 |
| `CLAUDE_CODE_PROXY_RESOLVES_HOSTS` | `false` | `true`: 프록시가 DNS 해석 수행 (호출자 대신) |

> **참고**: SOCKS 프록시는 지원되지 않습니다. Basic Auth는 URL에 포함 가능: `http://user:pass@proxy:port`

---

## 6. TLS / mTLS 인증서

기업 환경의 사설 인증서 및 상호 TLS 인증에 사용합니다.

| 변수 | 기본값 | 용도 |
|------|--------|------|
| `NODE_EXTRA_CA_CERTS` | None | 추가 CA 인증서 번들 경로 (PEM 형식). Node.js 표준 변수 |
| `CLAUDE_CODE_CLIENT_CERT` | None | mTLS 클라이언트 인증서 파일 경로 (PEM) |
| `CLAUDE_CODE_CLIENT_KEY` | None | mTLS 클라이언트 개인키 파일 경로 (PEM) |
| `CLAUDE_CODE_CLIENT_KEY_PASSPHRASE` | None | 암호화된 개인키의 비밀번호 |

---

## 7. Bash / 셸 실행

| 변수 | 기본값 | 용도 |
|------|--------|------|
| `BASH_DEFAULT_TIMEOUT_MS` | 120,000 (2분) | Bash 명령 기본 타임아웃 (밀리초) |
| `BASH_MAX_TIMEOUT_MS` | None | 모델이 설정할 수 있는 최대 타임아웃 |
| `BASH_MAX_OUTPUT_LENGTH` | None | 출력 중간 절삭 전 최대 문자 수 |
| `CLAUDE_CODE_SHELL` | 자동 감지 | 셸 명시적 지정. 로그인 셸과 작업 셸이 다를 때 유용 |
| `CLAUDE_CODE_SHELL_PREFIX` | None | 모든 Bash 명령에 적용할 프리픽스 커맨드 |
| `CLAUDE_CODE_GIT_BASH_PATH` | 자동 감지 | **Windows 전용**: Git Bash 실행파일 경로 |
| `CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR` | None | 각 Bash 명령 후 원래 작업 디렉터리로 복원 |
| `CLAUDE_ENV_FILE` | None | 각 Bash 명령 전에 소스(source)할 셸 스크립트 경로. 영구 환경 설정용 |

---

## 8. 컨텍스트 및 토큰 관리

| 변수 | 기본값 | 용도 |
|------|--------|------|
| `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` | ~95% | 자동 컨텍스트 압축 트리거 비율 (1-100) |
| `CLAUDE_CODE_FILE_READ_MAX_OUTPUT_TOKENS` | Default | 파일 읽기 시 토큰 한도 오버라이드 |
| `CLAUDE_CODE_MAX_OUTPUT_TOKENS` | 32,000 | 요청당 최대 출력 토큰 (최소 32K, 최대 64K) |
| `MAX_THINKING_TOKENS` | 31,999 | Extended Thinking 토큰 예산. `0`으로 비활성화 |
| `MAX_MCP_OUTPUT_TOKENS` | 25,000 | MCP 도구 응답 최대 토큰. 10,000 초과시 경고 |
| `SLASH_COMMAND_TOOL_CHAR_BUDGET` | 15,000 | 스킬(슬래시 커맨드) 메타데이터 최대 문자 수 |

---

## 9. MCP 서버 설정

| 변수 | 기본값 | 용도 |
|------|--------|------|
| `MCP_TIMEOUT` | None | MCP 서버 시작 타임아웃 (밀리초) |
| `MCP_TOOL_TIMEOUT` | None | MCP 도구 실행 타임아웃 (밀리초) |
| `MAX_MCP_OUTPUT_TOKENS` | 25,000 | MCP 도구 응답 최대 토큰 |
| `ENABLE_TOOL_SEARCH` | `auto` | MCP 도구 검색 동작. `auto`, `auto:N` (N=%), `true`, `false` |
| `MCP_OAUTH_CALLBACK_PORT` | None | MCP OAuth 인증 콜백 포트 |

---

## 10. 프롬프트 캐싱

비용 최적화를 위한 프롬프트 캐싱 제어입니다.

| 변수 | 기본값 | 용도 |
|------|--------|------|
| `DISABLE_PROMPT_CACHING` | `0` | `1`: **전체** 모델의 프롬프트 캐싱 비활성화 (개별 설정보다 우선) |
| `DISABLE_PROMPT_CACHING_HAIKU` | `0` | `1`: Haiku 모델만 캐싱 비활성화 |
| `DISABLE_PROMPT_CACHING_SONNET` | `0` | `1`: Sonnet 모델만 캐싱 비활성화 |
| `DISABLE_PROMPT_CACHING_OPUS` | `0` | `1`: Opus 모델만 캐싱 비활성화 |

---

## 11. 텔레메트리 및 개인정보

| 변수 | 기본값 | 용도 |
|------|--------|------|
| `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` | `0` | **마스터 스위치**: `1`로 설정 시 아래 4개 모두 비활성화 |
| `DISABLE_AUTOUPDATER` | `0` | `1`: 자동 업데이트 비활성화 |
| `DISABLE_BUG_COMMAND` | `0` | `1`: `/bug` 명령 비활성화 |
| `DISABLE_ERROR_REPORTING` | `0` | `1`: Sentry 오류 보고 비활성화 |
| `DISABLE_TELEMETRY` | `0` | `1`: Statsig 텔레메트리 비활성화 |
| `DISABLE_COST_WARNINGS` | `0` | `1`: 비용 경고 메시지 비활성화 |
| `DISABLE_NON_ESSENTIAL_MODEL_CALLS` | `0` | `1`: 비핵심 모델 호출 (flavor text 등) 비활성화 |
| `DISABLE_INSTALLATION_CHECKS` | `0` | `1`: 설치 경고 체크 비활성화 |

---

## 12. OpenTelemetry (엔터프라이즈)

엔터프라이즈 모니터링 및 사용량 추적을 위한 OpenTelemetry 설정입니다.

### 기본 설정

| 변수 | 기본값 | 용도 |
|------|--------|------|
| `CLAUDE_CODE_ENABLE_TELEMETRY` | `0` | `1`: OpenTelemetry 데이터 수집 활성화 |

### 메트릭 / 로그 내보내기

| 변수 | 기본값 | 용도 |
|------|--------|------|
| `OTEL_METRICS_EXPORTER` | None | 메트릭 내보내기: `console`, `otlp`, `prometheus` (쉼표 구분) |
| `OTEL_LOGS_EXPORTER` | None | 로그 내보내기: `console`, `otlp` (쉼표 구분) |
| `OTEL_EXPORTER_OTLP_PROTOCOL` | None | OTLP 프로토콜: `grpc`, `http/json`, `http/protobuf` |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | None | OTLP 컬렉터 엔드포인트 (예: `http://localhost:4317`) |
| `OTEL_EXPORTER_OTLP_HEADERS` | None | OTLP 인증 헤더 (예: `Authorization=Bearer token`) |

### 메트릭/로그별 오버라이드

| 변수 | 용도 |
|------|------|
| `OTEL_EXPORTER_OTLP_METRICS_PROTOCOL` | 메트릭 전용 프로토콜 오버라이드 |
| `OTEL_EXPORTER_OTLP_METRICS_ENDPOINT` | 메트릭 전용 엔드포인트 오버라이드 |
| `OTEL_EXPORTER_OTLP_LOGS_PROTOCOL` | 로그 전용 프로토콜 오버라이드 |
| `OTEL_EXPORTER_OTLP_LOGS_ENDPOINT` | 로그 전용 엔드포인트 오버라이드 |
| `OTEL_EXPORTER_OTLP_METRICS_CLIENT_KEY` | 메트릭 mTLS 클라이언트 키 |
| `OTEL_EXPORTER_OTLP_METRICS_CLIENT_CERTIFICATE` | 메트릭 mTLS 클라이언트 인증서 |

### 내보내기 주기 및 속성

| 변수 | 기본값 | 용도 |
|------|--------|------|
| `OTEL_METRIC_EXPORT_INTERVAL` | 60,000 (1분) | 메트릭 내보내기 주기 (밀리초) |
| `OTEL_LOGS_EXPORT_INTERVAL` | 5,000 (5초) | 로그 내보내기 주기 (밀리초) |
| `OTEL_LOG_USER_PROMPTS` | 비활성화 | `1`: 사용자 프롬프트 내용 로깅 (기본: 익명화) |
| `OTEL_RESOURCE_ATTRIBUTES` | None | 멀티팀 분류용 커스텀 속성 (예: `department=eng,team.id=platform`) |
| `OTEL_METRICS_INCLUDE_SESSION_ID` | `true` | 메트릭에 `session.id` 속성 포함 |
| `OTEL_METRICS_INCLUDE_VERSION` | `false` | 메트릭에 `app.version` 속성 포함 |
| `OTEL_METRICS_INCLUDE_ACCOUNT_UUID` | `true` | 메트릭에 `user.account_uuid` 속성 포함 |
| `CLAUDE_CODE_OTEL_HEADERS_HELPER_DEBOUNCE_MS` | 1,740,000 (29분) | 동적 OTel 헤더 갱신 주기 (밀리초) |

### 디버그 로깅

| 변수 | 용도 |
|------|------|
| `ANTHROPIC_LOG` | `debug`로 설정하여 디버그 로그 활성화 |
| `DEBUG` | 일반 상세 로깅 |
| `DEBUG_AUTH` | 인증 디버깅 |

---

## 13. UI 및 표시

| 변수 | 기본값 | 용도 |
|------|--------|------|
| `IS_DEMO` | `false` | `true`: 데모 모드 (이메일/org 숨김, 온보딩 생략) |
| `CLAUDE_CODE_HIDE_ACCOUNT_INFO` | `0` | `1`: UI에서 이메일 및 조직 정보 숨김 |
| `CLAUDE_CODE_DISABLE_TERMINAL_TITLE` | `0` | `1`: 대화 기반 터미널 제목 자동 업데이트 비활성화 |
| `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS` | `0` | `1`: 백그라운드 작업 전체 비활성화 (run_in_background, Ctrl+B) |
| `CLAUDE_CODE_ENABLE_TASKS` | `true` | `false`: 레거시 TODO 목록으로 전환 (TaskCreate 대신) |
| `DISABLE_MICROCOMPACT` | None | MicroCompact 출력 포맷/압축 비활성화 |

---

## 14. 파일 및 경로

| 변수 | 기본값 | 용도 |
|------|--------|------|
| `CLAUDE_CONFIG_DIR` | `~/.claude` | Claude Code 설정/데이터 저장 위치 커스터마이즈 |
| `CLAUDE_CODE_TMPDIR` | OS 기본 임시 경로 | 내부 임시 파일 디렉터리 오버라이드 (`/claude/` 자동 추가) |
| `CLAUDE_PROJECT_DIR` | 자동 감지 | 프로젝트 루트 디렉터리 오버라이드 |
| `CLAUDE_ENV_FILE` | None | Bash 명령마다 소스할 셸 스크립트 경로 |
| `CLAUDE_CODE_TASK_LIST_ID` | None | 세션간 공유 작업 목록 ID. 동일 ID로 멀티 인스턴스 협업 |
| `CLAUDE_CODE_EXIT_AFTER_STOP_DELAY` | None | 유휴 후 자동 종료 지연 (밀리초). SDK/자동화 환경용 |
| `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD` | `0` | `1`: `--add-dir` 디렉터리의 CLAUDE.md도 로드 |

---

## 15. 업데이트 및 기능 제어

| 변수 | 기본값 | 용도 |
|------|--------|------|
| `DISABLE_AUTOUPDATER` | `0` | `1`: 자동 업데이트 비활성화 |
| `FORCE_AUTOUPDATE_PLUGINS` | `false` | `true`: 플러그인 강제 자동 업데이트 |
| `USE_BUILTIN_RIPGREP` | `1` | `0`: 내장 ripgrep 대신 시스템 설치 `rg` 사용 |
| `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS` | `0` | `1`: `anthropic-beta` 헤더 비활성화. LLM 게이트웨이용 |
| `CLAUDE_CODE_IDE_SKIP_AUTO_INSTALL` | `0` | `1`: IDE 확장 자동 설치 생략 |

---

## 16. Hook 실행 컨텍스트 변수

Claude Code가 Hook 실행 시 **자동으로 설정**하는 변수입니다. 사용자가 직접 설정하지 않습니다.

| 변수 | 가용 위치 | 용도 |
|------|-----------|------|
| `CLAUDE_PROJECT_DIR` | 모든 Hook | 프로젝트 루트 절대 경로 |
| `CLAUDE_CODE_REMOTE` | 모든 Hook | 원격(웹) 환경이면 `"true"`, 로컬 CLI면 빈 값 |
| `CLAUDE_ENV_FILE` | SessionStart Hook | 영구 환경 변수 기록용 파일 경로 |
| `CLAUDE_FILE_PATHS` | 도구 관련 Hook | 관련 파일 경로 (공백 구분) |
| `CLAUDE_TOOL_NAME` | PreToolUse / PostToolUse | 현재 도구 이름 |
| `CLAUDE_TOOL_INPUT` | PreToolUse / PostToolUse | 도구 입력 (JSON 형식) |
| `CLAUDE_TOOL_OUTPUT` | PostToolUse만 | 도구 출력 (JSON 형식) |

---

## 17. SuperClaude 프레임워크 전용

SuperClaude 설치 시 사용되는 추가 환경 변수입니다.

### 프레임워크 설정

| 변수 | 기본값 | 용도 | 파일 |
|------|--------|------|------|
| `SUPERCLAUDE_PATH` | None | SuperClaude 컨텍스트 파일 경로 오버라이드 | `context_loader.py` |
| `CLAUDE_SESSION_ID` | 자동 생성 | 세션 식별 (hook 추적용) | `hook_tracker.py` |
| `CLAUDE_CONTEXT_INJECT` | `1` | 컨텍스트 주입 모드 (`1`=inject, `0`=directive) | `context_loader.py` |
| `CLAUDE_CONTEXT_MAX_TOKENS` | `8000` | 컨텍스트 로딩 최대 토큰 | `context_loader.py` |
| `CLAUDE_SHOW_SKILLS` | `1` | 스킬 요약 출력 토글 | `context_loader.py` |
| `CLAUDE_SKILL_POLL_INTERVAL` | `2.0` | 스킬 변경 감지 폴링 간격 (초) | `skill_watcher.py` |

### MCP 서버 API 키

| 변수 | MCP 서버 | 용도 |
|------|---------|------|
| `TAVILY_API_KEY` | Tavily | 웹 검색 API 키 ([app.tavily.com](https://app.tavily.com)) |
| `MORPH_API_KEY` | Morphllm | 패턴 기반 코드 수정 API 키 |
| `TWENTYFIRST_API_KEY` | Magic (21st.dev) | UI 컴포넌트 생성 API 키 |

---

## 18. 설정 파일 우선순위

환경 변수와 설정 파일 간의 우선순위입니다 (높은 순):

| 순위 | 범위 | Settings 파일 | MCP 설정 | CLAUDE.md |
|------|------|--------------|----------|-----------|
| 1 | **관리자** (시스템) | `managed-settings.json` | `managed-mcp.json` | N/A |
| 2 | **CLI 인수** | `--settings`, `--model` | `--mcp-config` | `--system-prompt` |
| 3 | **로컬** (gitignore됨) | `.claude/settings.local.json` | `~/.claude.json` | `.claude/CLAUDE.local.md` |
| 4 | **프로젝트** (커밋됨) | `.claude/settings.json` | `.mcp.json` | `CLAUDE.md` |
| 5 | **사용자** (개인) | `~/.claude/settings.json` | `~/.claude.json` | `~/.claude/CLAUDE.md` |

**관리자 설정 파일 경로:**
- macOS: `/Library/Application Support/ClaudeCode/`
- Linux/WSL: `/etc/claude-code/`
- Windows: `C:\Program Files\ClaudeCode\`

### settings.json의 주요 보완 옵션

| 키 | 타입 | 용도 |
|----|------|------|
| `model` | string | 기본 모델 (`ANTHROPIC_MODEL`과 동일) |
| `language` | string | 응답 언어 (예: `"korean"`) |
| `apiKeyHelper` | string | 동적 토큰 생성 스크립트 |
| `alwaysThinkingEnabled` | boolean | Extended Thinking 기본 활성화 |
| `env` | object | 세션별 환경 변수 설정 |
| `sandbox.enabled` | boolean | Bash 샌드박싱 활성화 |
| `permissions` | object | `allow/ask/deny` 권한 규칙 (와일드카드 지원) |
| `enableAllProjectMcpServers` | boolean | `.mcp.json` MCP 서버 자동 승인 |
| `hooks` | object | Pre/Post 도구 실행 Hook 정의 |
| `outputStyle` | string | 시스템 프롬프트 출력 스타일 조정 |
| `cleanupPeriodDays` | number | 비활성 세션 삭제 기간 (기본: 30일) |
| `plansDirectory` | string | 계획 파일 저장 경로 커스터마이즈 |

---

## 19. 참고 문헌

- [Claude Code 공식 문서](https://code.claude.com/docs/en/overview)
- [Settings 레퍼런스](https://code.claude.com/docs/en/settings)
- [Model Configuration](https://code.claude.com/docs/en/model-config)
- [Network Configuration](https://code.claude.com/docs/en/network-config)
- [LLM Gateway](https://code.claude.com/docs/en/llm-gateway)
- [Enterprise Deployment](https://code.claude.com/docs/en/third-party-integrations)
- [Monitoring & Usage](https://code.claude.com/docs/en/monitoring-usage)
- [Hooks Reference](https://code.claude.com/docs/en/hooks)
- [Amazon Bedrock](https://code.claude.com/docs/en/amazon-bedrock)
- [Google Vertex AI](https://code.claude.com/docs/en/google-vertex-ai)
- [CLI Reference](https://code.claude.com/docs/en/cli-reference)
- [Troubleshooting](https://code.claude.com/docs/en/troubleshooting)
- [GitHub 소스 분석 (환경 변수 220+)](https://gist.github.com/unkn0wncode/f87295d055dd0f0e8082358a0b5cc467)
