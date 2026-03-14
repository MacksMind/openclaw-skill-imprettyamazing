# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

This is an **OpenClaw skill** (not a traditional application). It defines instructions and API documentation that enable Claude to interact with [imprettyamazing.com](https://imprettyamazing.com) — a platform for tracking and celebrating accomplishments. There is no build system, no tests, and no application code. The deliverable is documentation (Markdown files) that gets published to [ClawHub](https://clawhub.ai) as the `imprettyamazing` skill.

## Repository Structure

- `SKILL.md` — The primary skill definition (frontmatter + instructions). This is what Claude receives when the skill is activated. It contains the authentication flow, API usage patterns, and behavioral rules.
- `references/api.md` — Complete API endpoint reference for `https://api.imprettyamazing.com`. SKILL.md references this for full endpoint details.
- `README.md` — Repository overview and maintenance notes.
- `.clawhubignore` — Files excluded from the ClawHub package (LICENSE, README.md, .env, .gitignore).
- `clawhub/` — Directory for ClawHub-specific files (currently empty).

## Key Concepts

- **Authentication**: Cookie-based auth via `POST /auth/login`. Session tokens (`access_token`, `refresh_token`) are persisted in a `TOOLS.md` file (outside this repo, in the user's workspace) with JWT expiry tracking. The skill never stores email/password.
- **Mutation confirmation**: All `POST`/`PATCH`/`DELETE` calls require explicit user confirmation before execution. `GET` requests are read-only and don't need confirmation.
- **STAR format**: Wins can optionally include Situation/Task/Action/Result structured data. All four fields are required when `starFormat` is provided.

## Making Changes

When modifying auth behavior or API details, update both `SKILL.md` and `references/api.md` together — they must stay in sync. After changes, validate against the live API with read-only smoke tests (`GET /auth/me`, `GET /wins/my-wins`).

The `SKILL.md` frontmatter (`name`, `description`) controls how the skill appears on ClawHub — keep the description actionable and specific about when to trigger the skill.
