# Feature — #ft-4 plugin-packaging

**File:** docs/features/ft-4-plugin-packaging.md
**Owner:** Marcus Chang
**TECH-SPECs:** spec-plugin-packaging.md (v1.0.0) — `docs/specs/spec-plugin-packaging.md`

---

## Stage B Discovery Findings

> Reference: `docs/discovery/disco-4.md`

### Test Impact Analysis

**Tests to Update:**
- `tests/hooks/test_log_event.py` — add test for `_handle_file_read` with populated `skill_paths`

**Tests to Add:**
- Plugin config validation: `plugin.json` required fields, `hooks.json` schema
- `log_event.py` fix: verify `resolve_skill_for_path` receives a populated `skill_paths` dict
- Dashboard skill: verify SKILL.md exists and contains expected content

**Coverage Gaps:**
- No existing test covers `resolve_skill_for_path` being called with `skill_paths=None` (the current bug)

### Existing Implementation Analysis

**Reusable Components:**
- `scripts/db.py` — as-is, already handles `${CLAUDE_PLUGIN_DATA}` fallback
- `scripts/skill_discovery.py` — as-is
- `scripts/inventory_snapshot.py` — as-is
- `dashboard/` — entire Django app unchanged

**Patterns to Follow:**
- VibeFlow plugin: `.claude-plugin/plugin.json` format, `hooks/hooks.json` format, `skills/` directory with SKILL.md

### Dependency & Side Effect Mapping

**Dependencies:**
- Claude Code plugin system — `claude plugin install`, `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_PLUGIN_DATA}`
- `uv` — required for running hook scripts (shebang: `#!/usr/bin/env -S uv run --script`)

**Breaking Changes:**
- Users who cloned the repo and use `.claude/settings.json` hooks are unaffected — those hooks remain for development
- Plugin consumers get hooks via `hooks/hooks.json` auto-registration

---

## Architecture Conformance

**Layer Assignment:**
- `.claude-plugin/plugin.json` — plugin metadata layer
- `hooks/hooks.json` — hook configuration layer (replaces manual `.claude/settings.json` for consumers)
- `skills/analytics-dashboard/SKILL.md` — user interaction layer
- `scripts/` — unchanged (data collection + data access layers)
- `dashboard/` — unchanged (presentation layer)

**Pattern Compliance:**
- Follows Claude Code plugin structure (same as vibeflow) ✓
- Uses `${CLAUDE_PLUGIN_ROOT}` for script references in hooks ✓
- Uses `${CLAUDE_PLUGIN_DATA}` for persistent storage ✓

---

## API Design

### .claude-plugin/plugin.json

- **Purpose:** Plugin metadata for `claude plugin install`
- **Format:** JSON object
- **Required Fields:**
  - `name`: `"skills-analytics"` — plugin identifier
  - `version`: `"1.0.0"` — semver version
  - `description`: `"Track and analyze Claude Code skill usage with a local dashboard"` — human-readable description
- **Optional Fields:**
  - `author`: `{ "name": "Marcus Chang" }`
  - `repository`: `"https://github.com/hardness1020/agent-skills-management"`
  - `license`: `"MIT"`
  - `keywords`: `["analytics", "skills", "dashboard", "usage-tracking"]`

### hooks/hooks.json

- **Purpose:** Declare hooks that Claude Code auto-registers on plugin install
- **Format:** JSON object with `description` and `hooks` keys
- **Hook Declarations:**
  - `PreToolUse` with matcher `"Skill|Read"` → `${CLAUDE_PLUGIN_ROOT}/scripts/log_event.py` (timeout: 10)
  - `UserPromptSubmit` (no matcher) → `${CLAUDE_PLUGIN_ROOT}/scripts/inventory_snapshot.py` (timeout: 10)

### skills/analytics-dashboard/SKILL.md

- **Purpose:** User-invocable `/analytics-dashboard` skill
- **Format:** Markdown with YAML frontmatter
- **Frontmatter:**
  ```yaml
  ---
  name: analytics-dashboard
  description: Launch the skills analytics dashboard to view usage metrics, scores, and trends
  metadata:
    triggers:
      - analytics dashboard
      - skill analytics
      - usage dashboard
      - open dashboard
  ---
  ```
- **Body:** Instructions for Claude to start the Django server:
  1. Run `cd "${CLAUDE_PLUGIN_ROOT}" && uv run python -m django runserver 8787 --settings=dashboard.analytics_project.settings` in background
  2. Tell the user the dashboard is available at `http://localhost:8787`
  3. Provide instructions to stop: Ctrl+C or kill the process

### log_event._handle_file_read() (fix)

- **Signature:** `_handle_file_read(conn: sqlite3.Connection, data: dict, tool_input: dict) -> None`
- **Purpose:** Log a nested file access if the file is inside a skill directory
- **Change:** Before calling `resolve_skill_for_path`, build `skill_paths` from `discover_all()`
- **New Logic:**
  ```python
  all_skills = skill_discovery.discover_all(project_dir=data.get("cwd", ""))
  skill_paths = {s["path"]: s for s in all_skills}
  result = skill_discovery.resolve_skill_for_path(file_path, skill_paths=skill_paths)
  ```
- **Returns:** None (writes to DB as side effect)

### settings._get_secret_key()

- **Signature:** `_get_secret_key() -> str`
- **Purpose:** Generate and persist a Django SECRET_KEY on first run
- **Behavior:**
  1. Resolve storage path: `${CLAUDE_PLUGIN_DATA}` or `~/.skills-analytics/`
  2. Check for `django_secret.txt` in that directory
  3. If exists: read and return
  4. If not: generate via `django.core.management.utils.get_random_secret_key()`, write to file, return

---

## Acceptance Criteria

### Plugin Structure
- [ ] `.claude-plugin/plugin.json` exists with `name`, `version`, `description` fields
- [ ] `hooks/hooks.json` exists with `PreToolUse` and `UserPromptSubmit` hook declarations
- [ ] `hooks/hooks.json` references scripts via `${CLAUDE_PLUGIN_ROOT}/scripts/`
- [ ] `skills/analytics-dashboard/SKILL.md` exists with valid frontmatter

### Hook Fix
- [ ] `log_event.py` `_handle_file_read` calls `discover_all()` to build `skill_paths`
- [ ] `log_event.py` passes populated `skill_paths` to `resolve_skill_for_path()`
- [ ] File reads inside skill directories are logged to `file_accesses` table
- [ ] File reads outside skill directories are not logged (no DB write)
- [ ] Hook still always outputs `permissionDecision: "allow"` regardless of errors

### Secret Key
- [ ] `settings.py` generates `SECRET_KEY` on first run and stores in `${CLAUDE_PLUGIN_DATA}/django_secret.txt`
- [ ] Subsequent runs reuse the stored key
- [ ] Falls back to `~/.skills-analytics/django_secret.txt` when `${CLAUDE_PLUGIN_DATA}` is unset

### Dashboard Skill
- [ ] `/analytics-dashboard` skill starts Django server on port 8787
- [ ] Dashboard is accessible at `http://localhost:8787` after skill runs

### Backward Compatibility
- [ ] `.claude/settings.json` is preserved for development use
- [ ] All existing 96 tests continue to pass

---

## Design Changes

### API Changes
- None — all existing API endpoints unchanged

### Schema Changes
- None — no DB schema changes

### Configuration Changes
- **NEW:** `.claude-plugin/plugin.json` — plugin metadata
- **NEW:** `hooks/hooks.json` — hook declarations
- **NEW:** `skills/analytics-dashboard/SKILL.md` — dashboard skill
- **MODIFIED:** `scripts/log_event.py` — bug fix for `resolve_skill_for_path`
- **MODIFIED:** `dashboard/analytics_project/settings.py` — SECRET_KEY generation

---

## Test & Eval Plan

### Unit Tests (Stage F)

- **`test_log_event.py` additions:**
  - Test `_handle_file_read` with a file path inside a skill directory → DB row inserted
  - Test `_handle_file_read` with a file path outside any skill directory → no DB write
  - Test `_handle_file_read` when `discover_all()` returns empty list → no error, no DB write

- **`test_plugin_config.py` (new):**
  - Test `plugin.json` has required fields (`name`, `version`, `description`)
  - Test `hooks.json` has valid structure with `PreToolUse` and `UserPromptSubmit`
  - Test hook commands reference `${CLAUDE_PLUGIN_ROOT}/scripts/`

- **`test_settings.py` (new):**
  - Test `_get_secret_key()` generates a key on first call
  - Test `_get_secret_key()` returns the same key on subsequent calls
  - Test `_get_secret_key()` uses `CLAUDE_PLUGIN_DATA` when set

### Integration Tests (Stage H)

- Simulate PreToolUse Read hook with `skill_paths` populated → verify `file_accesses` row
- Verify all 96 existing tests still pass

---

## Telemetry & Metrics

No new telemetry. The existing hook events (`skill_invoked`, `nested_file_accessed`, `skill_added`/`skill_removed`) continue to capture all usage data. The `resolve_skill_for_path` fix means `nested_file_accessed` events will now actually be recorded (previously silently dropped).

---

## Edge Cases & Risks

| Edge Case | Handling |
|-----------|---------|
| `discover_all()` slow on large skill sets | Accept 10-50ms overhead; optimize with caching later if needed |
| `${CLAUDE_PLUGIN_ROOT}` not set (running outside plugin) | Scripts fall back to `_PROJECT_ROOT` from `__file__` |
| `${CLAUDE_PLUGIN_DATA}` not set | `db.get_connection()` falls back to `~/.skills-analytics/` |
| Django SECRET_KEY file permissions | Standard user file permissions; no special handling needed |
| Plugin installed at project scope instead of user scope | Hooks only fire in that project — works but limited. Document user scope as recommended |

---

## References

- Discovery: `docs/discovery/disco-4.md`
- Tech Spec: `docs/specs/spec-plugin-packaging.md`
- ADR: `docs/adrs/adr-1-plugin-packaging.md`
- VibeFlow plugin reference: `~/.claude/plugins/cache/vibeflow/vibeflow/1.0.0/`
