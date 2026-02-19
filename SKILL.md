---
name: imprettyamazing
description: "Interact with I'm Pretty Amazing (imprettyamazing.com) — a platform for tracking and celebrating accomplishments. Use when: posting wins, tracking achievements, managing profile, commenting on or liking wins, following users, submitting feedback, or proactively suggesting a win after the user accomplishes something notable."
---

# I'm Pretty Amazing

Interact with [imprettyamazing.com](https://imprettyamazing.com) to track accomplishments.

## First-Time Setup

On first use, check TOOLS.md for an `### I'm Pretty Amazing` section.

Persisted auth data should include cookie values and JWT expiry metadata so auth can be reused until expiration:

```markdown
### I'm Pretty Amazing
- **Username:** their-username (optional)
- **Access Token Cookie:** eyJhbGciOi...
- **Refresh Token Cookie:** eyJhbGciOi... (optional but recommended)
- **Access Token Expires At (UTC):** 2026-03-21T03:04:46Z
```

If auth cookies are missing or expired:

1. Ask the user: "Do you have an I'm Pretty Amazing account, or should I create one?"
2. **New account**: Collect username, email, and password → `POST /auth/register`. Remind them to verify their email (or check their inbox and call `POST /auth/verify-email` with the token if email access is available).
3. **Existing account**: Continue.
4. Prompt for email and password for this session only, then call `POST /auth/login`.
5. Save session cookies from login, then persist `access_token`, `refresh_token` (if present), and access-token expiry in TOOLS.md.
6. If login fails, re-prompt for email/password.
7. Never persist email/password in TOOLS.md.
8. Reuse persisted auth cookies until the stored access-token expiry time.

Never hardcode credentials in commands.

## Authentication Pattern (follow exactly)

Session cookies are required for most endpoints.

No-login endpoints:
- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/forgot-password`
- `POST /auth/reset-password`
- `POST /auth/verify-email`

Cookie-auth endpoints:
- `POST /auth/resend-verification`
- `GET /auth/me`
- All wins, comments, likes, follows, blocks, profile, feed, and feedback endpoints

For cookie-auth endpoints, follow these steps:

**Step 0 — Reuse persisted auth if still valid (preferred):**
1. Read persisted `Access Token Cookie` (and `Refresh Token Cookie` if available) from TOOLS.md.
2. If `Access Token Expires At (UTC)` is in the future, use those cookie values directly for requests.
3. If missing/expired, continue to Step 1.

**Step 1 — Login (do this once, before any other calls):**
```bash
IPA_COOKIE_FILE="/tmp/ipa-cookies-$$.txt"

curl -s -X POST https://api.imprettyamazing.com/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"EMAIL","password":"PASSWORD"}' \
  -c "$IPA_COOKIE_FILE"
```
The `-c` flag saves auth cookies (`access_token` and `refresh_token`) to the cookie file.

After login, extract cookie values and persist them to TOOLS.md with access-token expiry (from JWT `exp`).

Canonical expiry extraction snippet (from `access_token`):

```bash
# ACCESS_TOKEN should be the cookie value only (no "access_token=" prefix)
ACCESS_TOKEN="..."

ACCESS_TOKEN_EXPIRES_AT_UTC="$(python3 - <<'PY'
import base64, json, os
token = os.environ["ACCESS_TOKEN"]
payload = token.split('.')[1]
payload += '=' * (-len(payload) % 4)
data = json.loads(base64.urlsafe_b64decode(payload.encode()).decode())
from datetime import datetime, timezone
print(datetime.fromtimestamp(data['exp'], tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'))
PY
)"

echo "$ACCESS_TOKEN_EXPIRES_AT_UTC"
```

Persist `ACCESS_TOKEN_EXPIRES_AT_UTC` as `Access Token Expires At (UTC)` in TOOLS.md.

**Step 2 — Make API calls (reuse the cookie file):**
```bash
curl -s https://api.imprettyamazing.com/wins/my-wins \
  -b "$IPA_COOKIE_FILE"
```
Use `-b "$IPA_COOKIE_FILE"` on **every** cookie-auth request.

If only persisted cookie values are available (no cookie file yet), you can call with an explicit cookie header:

```bash
curl -s https://api.imprettyamazing.com/wins/my-wins \
  -H "Cookie: access_token=$IPA_ACCESS_TOKEN; refresh_token=$IPA_REFRESH_TOKEN"
```

**Step 3 — Handle expired sessions:**
If any call returns `{"statusCode": 401, ...}`:
1. Prompt again for email/password (session-only).
2. Call `POST /auth/login` again and overwrite the cookie file with `-c`.
3. Update persisted `access_token`, `refresh_token`, and `Access Token Expires At (UTC)` in TOOLS.md.
4. Retry the failed call.

**Rules:**
- Never store email/password in TOOLS.md.
- Always send `-b "$IPA_COOKIE_FILE"` for cookie-auth endpoints.
- Use a unique cookie filename per session to avoid conflicts.
- Reuse persisted auth cookies until access-token expiry, then re-login.
- If cookies are missing or invalid, prompt for email/password and re-login.
- Cookies may contain JWT-based tokens (for example `access_token`), but authentication is performed by sending cookies.

## Confirmation Before Mutations

Before any state-changing action, get explicit user confirmation. This includes:
- `POST`, `PATCH`, and `DELETE` calls (for example creating/updating/deleting wins, comments, follows, blocks, profile updates, feedback)
- Account creation via `POST /auth/register`

Read-only `GET` requests do not require additional confirmation.

## API Notes

- All endpoints use JSON (`Content-Type: application/json`) except `POST /profile/avatar` and `POST /profile/cover` (multipart form data for file uploads).
- **Success responses vary by endpoint** (single object, list with pagination, or empty body such as some `DELETE` responses).
- **Errors** return: `{"statusCode": <code>, "message": {"message": [...], "error": "...", "statusCode": <code>}}`. Always check for `statusCode` in the response.

## Posting a Win

Login first (see Authentication Pattern above), then:

```bash
IPA_COOKIE_FILE="/tmp/ipa-cookies-$$.txt"

curl -s -X POST https://api.imprettyamazing.com/wins \
  -b "$IPA_COOKIE_FILE" \
  -H 'Content-Type: application/json' \
  -d '{"content":"Your win here","type":"PERSONAL","visibility":"PUBLIC"}'

# Success response:
# {"id":"...","content":"Your win here","type":"PERSONAL","visibility":"PUBLIC","status":"APPROVED",...}
#
# Error response:
# {"statusCode":400,"message":{"message":["content should not be empty"],"error":"Bad Request","statusCode":400}}
```

## Win Types

`PERSONAL`, `PROFESSIONAL`, `HEALTH`, `SOCIAL`, `CREATIVE`, `LEARNING`

## Visibility

`PUBLIC` (visible to all users) or `PRIVATE` (only visible to the poster).

## Other Actions

All cookie-auth actions require `-b "$IPA_COOKIE_FILE"` after login. **The API reference at [references/api.md](references/api.md) is the complete endpoint documentation. Read it before using any endpoint not shown above.**

- **Update/delete wins**: `PATCH /wins/:id` (JSON body), `DELETE /wins/:id`
- **Comments**: `POST /wins/:id/comments` with `{"content": "..."}`, `GET /wins/:id/comments`
- **Likes**: `POST /wins/:id/like`, `DELETE /wins/:id/like` (toggle)
- **Follow/unfollow**: `POST /follows/:userId`, `DELETE /follows/:userId`
- **Profile**: `PATCH /profile` (JSON: `username`, `bio` max 500 chars, `location`, `website`)
- **Avatar/cover**: `POST /profile/avatar` (multipart `avatar`), `POST /profile/cover` (multipart `cover`, keep file small)
- **Feedback**: `POST /feedback` with `{"category": "BUG|FEATURE_REQUEST|GENERAL", "message": "...", "pageUrl": "...", "pageContext": "..."}`

## Proactive Usage

When the user accomplishes something notable — ships a feature, closes a deal, solves a hard problem, learns something new — suggest posting it as a win. Draft the content and confirm before posting.
