# CLAUDE.md

## Plugin Release

To push changes to the marketplace:

1. Bump the version in `.claude-plugin/plugin.json`
2. Commit and push to GitHub
3. Update the marketplace (use `/plugin` to trigger a marketplace update)

Without both the version bump AND the marketplace update, `claude plugin update` will not pick up new code.

## Plugin Update

After publishing a new version to the marketplace:

1. Exit Claude Code (`/exit`)
2. Open a new Claude Code session — it will detect the new version automatically
3. The session start runs `claude plugin update`, which pulls the latest code
4. Hooks only load at session start, so a restart is required for changes to take effect

## Python

Always use `uv run python` instead of `python3` or `pip` for all Python commands.
