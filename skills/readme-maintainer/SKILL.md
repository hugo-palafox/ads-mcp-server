---
name: readme-maintainer
description: Keep README.md accurate, installable, and onboarding-friendly. Use when project capabilities, dependencies, or setup steps change.
---

# Readme Maintainer

Keep `README.md` accurate and onboarding-friendly.

## Workflow

1. Verify the install command (`pip install -e .`) works end-to-end.
2. Verify the quick-start example produces the expected output.
3. Check feature list matches the current state of `cli/main.py` and `mcp_app/server.py`.

## Rules

- Badges (CI, license, Python version) must link to live status URLs.
- Install instructions must reflect the current packaging config in `pyproject.toml`.
- Quick-start example must use a realistic machine config (matching `data/machines/` files if committed).
- Feature bullets must match the actual CLI commands and MCP tools.
- Update the "What It Does" summary when new major capabilities are added.
- Keep section ordering: Title → Badges → What It Does → Quick Start → Features → Development → License.
- Reference the docs/ folder for detailed documentation rather than duplicating content inline.
- Verify all links work (no broken anchors or relative paths).
