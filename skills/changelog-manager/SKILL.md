---
name: changelog-manager
description: Manage CHANGELOG.md entries by appending new release sections. Use when a feature, fix, or change needs to be recorded in the changelog after implementation.
---

# Changelog Manager

Append new entries to `CHANGELOG.md` — never rewrite prior history.

## Format

Each release follows the template:

```markdown
## <version> - <YYYY-MM-DD>

### Added
- <new features, tools, commands>

### Changed
- <behavior changes, refactors, renames>

### Fixed
- <bug fixes>

### Removed
- <deleted features, files>

### Notes
- <migration notes, caveats, context>
```

Use `## 0.1.3 - 2026-03-06` style headers. Use `- N/A` for empty sections.

## Rules

1. Derive the next version from the latest `CHANGELOG.md` header (patch bump by default; minor for new public interfaces).
2. Never rewrite or delete prior entries — only append.
3. Use present tense, imperative style ("Add" not "Added feature X").
4. Reference file paths for changes (e.g. `ads/beckhoff_client.py`).
5. Keep descriptions brief — one line per entry.
6. Place the new section at the top of the file, above all existing entries.
7. After writing, verify: `git diff CHANGELOG.md` shows only the new section prepended.
