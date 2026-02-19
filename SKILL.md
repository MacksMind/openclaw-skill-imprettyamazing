---
name: imprettyamazing
description: "Interact with I'm Pretty Amazing (imprettyamazing.com) — a platform for tracking and celebrating accomplishments. Use when: posting wins, tracking achievements, managing profile, commenting on or liking wins, following users, submitting feedback, or proactively suggesting a win after the user accomplishes something notable."
---

# I'm Pretty Amazing

Interact with [imprettyamazing.com](https://imprettyamazing.com) to track accomplishments.

## First-Time Setup

On first use, check TOOLS.md for an `### I'm Pretty Amazing` section with email and password.

If credentials are missing:

1. Ask the user: "Do you have an I'm Pretty Amazing account, or should I create one?"
2. **New account**: Collect username, email, and password → `POST /auth/register`. Remind them to verify their email (or check their inbox and call `POST /auth/verify-email` with the token if email access is available).
3. **Existing account**: Collect email and password.
4. Verify credentials work → `POST /auth/login`. If login fails, re-prompt.
5. Save to TOOLS.md:

```markdown
### I'm Pretty Amazing
- **Email:** user@example.com
- **Password:** (stored)
- **Username:** their-username
```

Never hardcode credentials in commands — always read from TOOLS.md.

## Authentication Pattern (follow exactly)

Every API call (except login/register) requires cookies from a prior login. Follow these steps:

**Step 1 — Login (do this once, before any other calls):**
```bash
curl -s -X POST https://api.imprettyamazing.com/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"EMAIL","password":"PASSWORD"}' \
  -c /tmp/ipa-cookies.txt
```
The `-c` flag **saves** the authentication cookies to the file.

**Step 2 — Make API calls (reuse the same cookie file):**
```bash
curl -s -b /tmp/ipa-cookies.txt https://api.imprettyamazing.com/wins/my-wins
```
The `-b` flag **sends** the saved cookies. Use `-b /tmp/ipa-cookies.txt` on **every** subsequent call.

**Step 3 — Handle expired sessions:**
If any call returns `{"statusCode": 401, ...}`, go back to Step 1 (re-login), then retry the failed call.

**Rules:**
- Always use `-c` on login and `-b` on every other call. Same filename.
- Use a unique cookie filename per session (e.g. `/tmp/ipa-cookies-12345.txt`) to avoid conflicts.
- Never skip the login step. Calls without `-b` will fail with 401.

## API Notes

- All endpoints use JSON (`Content-Type: application/json`) except `POST /profile/avatar` and `POST /profile/cover` (multipart form data for file uploads).
- **Success** returns the created/updated object as JSON.
- **Errors** return: `{"statusCode": <code>, "message": {"message": [...], "error": "...", "statusCode": <code>}}`. Always check for `statusCode` in the response.

## Posting a Win

Login first (see Authentication Pattern above), then:

```bash
curl -s -X POST https://api.imprettyamazing.com/wins \
  -b /tmp/ipa-cookies.txt \
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

All require login cookies first. **The API reference at [references/api.md](references/api.md) is the complete endpoint documentation. Read it before using any endpoint not shown above.**

- **Update/delete wins**: `PATCH /wins/:id` (JSON body), `DELETE /wins/:id`
- **Comments**: `POST /wins/:id/comments` with `{"content": "..."}`, `GET /wins/:id/comments`
- **Likes**: `POST /wins/:id/like`, `DELETE /wins/:id/like` (toggle)
- **Follow/unfollow**: `POST /follows/:userId`, `DELETE /follows/:userId`
- **Profile**: `PATCH /profile` (JSON: `username`, `bio` max 500 chars, `location`, `website`)
- **Avatar/cover**: `POST /profile/avatar` (multipart `avatar`), `POST /profile/cover` (multipart `cover`, keep file small)
- **Feedback**: `POST /feedback` with `{"category": "BUG|FEATURE_REQUEST|GENERAL", "message": "...", "pageUrl": "...", "pageContext": "..."}`

## Proactive Usage

When the user accomplishes something notable — ships a feature, closes a deal, solves a hard problem, learns something new — suggest posting it as a win. Draft the content and confirm before posting.
