# OpenClaw Skill: I’m Pretty Amazing

This repository defines an OpenClaw skill for interacting with [imprettyamazing.com](https://imprettyamazing.com), including wins, comments, likes, follows, profile updates, and feedback.

## Repository Layout

- `SKILL.md` — primary skill instructions and operational behavior
- `references/api.md` — endpoint reference and payload notes

## Authentication Model

The skill uses **cookie-based authentication**:

- Login via `POST /auth/login`
- Save cookies with curl `-c` (cookie jar)
- Send cookies on authenticated requests with curl `-b`
- If a request returns `401`, re-login and retry

### Required Environment Variables

Cookie-auth workflows assume the following environment variables are available (typically sourced from persisted values in `TOOLS.md`):

- `IPA_ACCESS_TOKEN`
- `IPA_REFRESH_TOKEN` (optional for some sessions, but required by declared skill metadata)
- `IPA_ACCESS_TOKEN_EXPIRES_AT_UTC`

### Persisted Auth Metadata

To reduce repeated logins, persist auth metadata in `TOOLS.md` under:

```md
### I'm Pretty Amazing
- **Username:** <optional>
- **Access Token Cookie:** <access_token cookie value>
- **Refresh Token Cookie:** <optional refresh_token cookie value>
- **Access Token Expires At (UTC):** <ISO timestamp>
```

Notes:
- Do **not** persist email/password.
- Cookies may contain JWTs; expiry is derived from the JWT `exp` claim.
- Reuse persisted cookie values until `Access Token Expires At (UTC)`.
- Treat persisted `access_token`/`refresh_token` values as sensitive credentials that permit authenticated actions on behalf of the user.
- Never commit token values to repository files, and never print full token values in logs or chat output.

## Safety Rules

- Require explicit user confirmation before any mutating `POST`/`PATCH`/`DELETE` action.
- `GET` requests are read-only and do not require extra confirmation.

## Known Live Validation (Feb 18, 2026)

Read-only smoke checks passed with cookie auth:

- `GET /auth/me` → `200`
- `GET /wins/my-wins` → `200`

Observed in live behavior:
- Login sets `access_token` / `refresh_token` via `Set-Cookie`.

## Updating This Skill

When changing auth behavior, update both files together:

1. `SKILL.md`
2. `references/api.md`

Then run a quick read-only smoke test to confirm docs match production behavior.
