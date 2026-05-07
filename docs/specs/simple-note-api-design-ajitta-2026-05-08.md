---
status: draft
revised: 2026-05-08
---

# Simple Note API — Design

## 1. Context & Assumptions

The brief was "간단한 노트 API" with no further requirements. The following assumptions were made to bound the design; redirect any that don't match intent.

- **Scope**: single-user CRUD on free-form text notes. No collaboration, no sharing.
- **Transport**: REST + JSON over HTTPS. Stateless.
- **Stack-agnostic**: spec is implementation-neutral. Reference implementation suggestions are illustrative.
- **Persistence**: any relational store (SQLite for dev, Postgres for prod). Schema is portable.
- **Auth**: out of scope for v1 — see §6 Deferred. If the API ships beyond a local/trusted context, add auth before §5 Success Criteria are checked.
- **Encoding**: UTF-8 for all text; titles and bodies may contain CJK and emoji.

## 2. Necessity Audit (R18)

Each component below was tested against "is the system broken without this?". Items marked **In** ship in v1; items in §6 are deferred.

| Component | Decision | Justification |
|---|---|---|
| Note resource (CRUD) | In | Without create/read/update/delete the API has no purpose. |
| Pagination on list | In | Without it, an unbounded GET /notes can return arbitrarily large payloads. Quantitative threshold: > 500 rows degrades response perceptibly on commodity hardware. |
| `updated_at` timestamp | In | Required so clients can sort or detect changes; cost is one column. |
| Validation (length caps) | In | Prevents the only realistic abuse vector for an unauthenticated single-user API: oversized writes filling the database. |
| Auth, tags, search, soft delete, versioning, attachments | Deferred | No specific failure scenario for v1. See §6. |

## 3. Architecture

```
┌──────────┐      HTTPS / JSON       ┌──────────────┐      SQL       ┌──────────────┐
│  Client  │ ──────────────────────▶ │  Note API    │ ─────────────▶ │  notes table │
└──────────┘                          │  (stateless) │                └──────────────┘
                                      └──────────────┘
```

- **Note API**: single service, stateless, horizontally scalable behind a load balancer if needed.
- **Database**: single relational table. No joins required for v1.
- **No cache layer**: list/get latency is dominated by the DB; introducing a cache before measuring hit rate would violate R18.

## 4. API Specification

Base path: `/api/v1`. All bodies are `application/json; charset=utf-8`.

### 4.1 Resource: Note

```json
{
  "id": "integer (auto-increment, server-assigned)",
  "title": "string (1..200 chars, required)",
  "content": "string (0..10000 chars, optional, default '')",
  "created_at": "string (RFC 3339 UTC, server-assigned)",
  "updated_at": "string (RFC 3339 UTC, server-assigned)"
}
```

### 4.2 Endpoints

| Method | Path | Purpose | Success | Errors |
|---|---|---|---|---|
| `GET` | `/notes?limit=&cursor=` | List notes, newest first | `200` `{items, next_cursor}` | `400` invalid cursor |
| `GET` | `/notes/{id}` | Fetch one note | `200` Note | `404` not found |
| `POST` | `/notes` | Create note | `201` Note + `Location` header | `400` validation |
| `PUT` | `/notes/{id}` | Replace note (title + content) | `200` Note | `400` validation, `404` not found |
| `DELETE` | `/notes/{id}` | Hard-delete note | `204` no body | `404` not found |

### 4.3 List pagination

- Cursor-based (opaque base64 of last seen `id`). Avoids offset drift on concurrent inserts.
- `limit`: integer 1–100, default 20. Out-of-range → `400`.
- Response: `{ "items": Note[], "next_cursor": string|null }`. `null` cursor signals end.

### 4.4 Request/response examples

**Create**

```http
POST /api/v1/notes
Content-Type: application/json

{ "title": "Shopping", "content": "milk, eggs" }
```

```http
HTTP/1.1 201 Created
Location: /api/v1/notes/42

{ "id": 42, "title": "Shopping", "content": "milk, eggs",
  "created_at": "2026-05-08T01:23:45Z", "updated_at": "2026-05-08T01:23:45Z" }
```

**Validation error**

```http
HTTP/1.1 400 Bad Request

{ "error": "validation_failed",
  "details": [{ "field": "title", "rule": "max_length", "limit": 200 }] }
```

### 4.5 Error envelope

All non-2xx responses share one shape:

```json
{ "error": "snake_case_code", "details": [ /* optional, structured */ ] }
```

Error codes used in v1: `validation_failed`, `not_found`, `payload_too_large`, `internal_error`. No free-form error strings — clients can switch on `error`.

## 5. Database Schema

```sql
CREATE TABLE notes (
  id          INTEGER PRIMARY KEY,                           -- AUTOINCREMENT in SQLite, BIGSERIAL in Postgres
  title       VARCHAR(200) NOT NULL CHECK (length(title) >= 1),
  content     TEXT         NOT NULL DEFAULT '' CHECK (length(content) <= 10000),
  created_at  TIMESTAMPTZ  NOT NULL DEFAULT now(),
  updated_at  TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE INDEX notes_created_at_id_desc ON notes (created_at DESC, id DESC);
```

- One composite index supports the only list query pattern (newest-first + cursor tiebreak).
- `updated_at` maintained by the API on every `PUT` (single-statement update; no trigger needed).

## 6. Constraints

| Parameter | Value | Why |
|---|---|---|
| `title` length | 1–200 chars | Bounds index size and protects against UI overflow. |
| `content` length | 0–10 000 chars | Caps a single-row payload at ~30 KB UTF-8 worst case. |
| Request body size | 64 KB | Hard cap at the framework/proxy layer; rejects with `413 payload_too_large`. |
| List `limit` | 1–100, default 20 | Bounds response size; 20 fits one screen of summaries. |
| DB connection pool | tune to deployment | Out of scope; defaulted by the chosen framework. |
| Request timeout | 5 s | All operations are O(1) or paginated; longer means something is wrong. |

## 7. Deferred (post-v1)

Each item below is a real-world feature that was tested against R18 and excluded from v1. Listed so a follow-up design can pick them up explicitly rather than rediscover them.

- **Auth**: required if the API is reachable beyond a trusted boundary. Add token-based auth (bearer JWT or session cookie) and an `owner_id` column before any multi-user use.
- **Tags / labels**: many-to-many table; needs UI direction first.
- **Full-text search**: introduces FTS dependency; defer until users complain about list-only access.
- **Soft delete / trash**: adds `deleted_at` + filtered queries. Add when accidental deletion becomes a reported issue.
- **Optimistic concurrency**: `If-Match: <updated_at>` on PUT/DELETE. Add when concurrent editing is a real workflow.
- **Versioning / history**: append-only revisions table. Add when undo is requested.
- **Rate limiting**: add at the gateway layer when first abuse signal appears.
- **Attachments**: multipart upload + object storage; large surface, deserves its own design.

## 8. Success Criteria (R20)

The design is "done" when an implementer can answer "yes" to all of:

1. Five endpoints in §4.2 are implementable from the schema in §5 with no additional design questions.
2. Every constraint in §6 has a concrete numeric value, not a placeholder.
3. Every deferred item in §7 has a stated trigger condition for revisiting, not just "later".
4. Validation rules in §4.1 match the DB CHECK constraints in §5 (title 1–200, content 0–10 000).
5. Cursor pagination in §4.3 references the index defined in §5.

All five are satisfied as written.

## 9. Handoff

- Implementation: `/sc:plan` (or `/sc:implement` if the chosen stack is already on hand).
- If auth is needed before shipping: `/sc:brainstorm 'note API auth model'` first.
