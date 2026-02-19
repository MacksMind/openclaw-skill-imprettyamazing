---
name: imprettyamazing
description: "Interact with I'm Pretty Amazing (imprettyamazing.com) — a platform for tracking and celebrating accomplishments. Use when: posting wins, tracking achievements, managing profile, commenting on or liking wins, following users, submitting feedback, or proactively suggesting a win after the user accomplishes something notable."
---

# I'm Pretty Amazing

Interact with [imprettyamazing.com](https://imprettyamazing.com) to track accomplishments.

## Credentials

Requires email and password. Check TOOLS.md or workspace config for credentials. Never hardcode credentials in commands.

## Posting a Win

Use the bundled script (no dependencies beyond Python stdlib):

```bash
python3 scripts/post_win.py \
  --email "user@example.com" \
  --password "password" \
  --content "Description of the win" \
  --type PERSONAL \
  --visibility PUBLIC
```

Or call the API directly with `curl`:

```bash
# Login (captures cookies)
curl -s -X POST https://api.imprettyamazing.com/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"...","password":"..."}' \
  -c /tmp/ipa-cookies.txt

# Post win
curl -s -X POST https://api.imprettyamazing.com/wins \
  -b /tmp/ipa-cookies.txt \
  -F 'content=Your win here' \
  -F 'type=PERSONAL' \
  -F 'visibility=PUBLIC'
```

## Win Types

`PERSONAL`, `PROFESSIONAL`, `HEALTH`, `SOCIAL`, `CREATIVE`, `LEARNING`

## Visibility

`PUBLIC` (visible to all users) or `PRIVATE` (only visible to the poster).

## Other Actions

All require login cookies first. See [references/api.md](references/api.md) for full details.

- **Update/delete wins**: `PATCH /wins/:id` (JSON body), `DELETE /wins/:id`
- **Comments**: `POST /wins/:id/comments` with `{"content": "..."}`, `GET /wins/:id/comments`
- **Likes**: `POST /wins/:id/like`, `DELETE /wins/:id/like` (toggle)
- **Follow/unfollow**: `POST /follows/:userId`, `DELETE /follows/:userId`
- **Profile**: `PATCH /profile` (JSON: `username`, `bio` max 500 chars, `location`, `website`)
- **Avatar/cover**: `POST /profile/avatar` (multipart `avatar`), `POST /profile/cover` (multipart `cover`, keep file small)
- **Feedback**: `POST /feedback` with `{"category": "BUG|FEATURE_REQUEST|GENERAL", "message": "...", "pageUrl": "...", "pageContext": "..."}`

## Proactive Usage

When the user accomplishes something notable — ships a feature, closes a deal, solves a hard problem, learns something new — suggest posting it as a win. Draft the content and confirm before posting.
