# CLAUDE.md

This file provides guidance to Claude Code and other AI assistants working in this repository.

---

## Repository Overview

| Property | Value |
|----------|-------|
| **Owner** | sellis-collab |
| **Remote** | `http://local_proxy@127.0.0.1:37855/git/sellis-collab/Testing` |
| **Default branch** | `main` |
| **Status** | Newly initialized — no source code yet |

This repository was initialized in February 2026 and currently contains only a `.gitkeep` placeholder. All sections marked with `<!-- TODO -->` below should be updated as the project evolves.

---

## Project Structure

<!-- TODO: Update this section once source code is added. -->

```
Testing/
├── .gitkeep          # placeholder — remove once real files exist
└── CLAUDE.md         # this file
```

---

## Development Setup

<!-- TODO: Add setup instructions once a tech stack is chosen. -->

No build tools, package managers, linters, test runners, or CI/CD pipelines have been configured yet. When they are, document them here with:

- Prerequisites (runtime versions, system dependencies)
- Installation command
- Environment variable requirements (`.env.example` or equivalent)

---

## Common Commands

<!-- TODO: Replace placeholders with real commands once the stack is defined. -->

| Task | Command |
|------|---------|
| Install dependencies | _not yet configured_ |
| Run development server | _not yet configured_ |
| Build for production | _not yet configured_ |
| Run tests | _not yet configured_ |
| Run linter | _not yet configured_ |
| Format code | _not yet configured_ |

---

## Git Workflow

### Branch conventions

- **`main`** — default/stable branch; never push directly
- **`master`** — local alias pointing to the same commit as `main`
- **`claude/<task-description>-<session-id>`** — all AI-driven feature branches

  Example: `claude/add-claude-documentation-W4fzC`

### Rules

1. All development must happen on the designated `claude/` branch for the session.
2. Never push directly to `main` or `master`.
3. Always set upstream on first push: `git push -u origin <branch-name>`
4. On network failures, retry push with exponential backoff: 2 s → 4 s → 8 s → 16 s (max 4 retries).
5. A push will fail with HTTP 403 if the branch name does not follow the `claude/` prefix convention.

### Commit message style

- Use the imperative mood: "Add feature" not "Added feature"
- Keep the subject line under 72 characters
- Reference issue numbers where relevant

---

## Code Conventions

<!-- TODO: Update once a language/framework is chosen. -->

No code conventions are established yet. When they are, document:

- Language version and runtime
- Formatting tool and configuration (e.g., Prettier, Black, rustfmt)
- Linting rules
- Naming conventions (files, variables, functions, types)
- Test file location and naming pattern

---

## AI Assistant Guidelines

The following rules apply to all AI assistants (Claude Code and others) working in this repository:

### General behaviour

- Always develop on the branch designated for the current session (`claude/<task>-<id>`).
- Read files before editing them. Understand existing code before proposing changes.
- Prefer editing existing files over creating new ones.
- Only create files that are strictly necessary for the task.
- Avoid over-engineering: match the scope of changes exactly to what was requested.
- Do not add comments, docstrings, or type annotations to code you did not change.
- Do not add error handling or validation for scenarios that cannot occur.
- Do not introduce security vulnerabilities (injection, XSS, insecure secrets, etc.).

### Risky actions — ask before proceeding

The following require explicit user confirmation before execution:

- Deleting files or branches
- Force-pushing (`--force`)
- `git reset --hard`
- Modifying CI/CD pipelines
- Pushing to `main` / `master`
- Any action that is hard to reverse or affects shared state

### When blocked

Do not retry the same failing action repeatedly. Diagnose the root cause, try an alternative approach, or ask the user for guidance.

---

## Updating This File

This file should be kept current as the project evolves. Update it whenever:

- A tech stack is chosen or changed
- New tooling is added (linters, formatters, test frameworks, CI/CD)
- Branching or commit conventions change
- Significant architectural decisions are made
