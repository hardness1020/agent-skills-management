"""Skill discovery module.

Scans all skill sources (folder-based and plugin-based) and returns
a unified list of SkillInfo dicts. Also provides file classification
and path-to-skill resolution.
"""


def discover_all(project_dir: str = None) -> list[dict]:
    """Scan all skill sources and return a deduplicated list of SkillInfo dicts."""
    raise NotImplementedError


def discover_folder_skills(skills_dir: str, scope: str) -> list[dict]:
    """Scan a .claude/skills/ directory for folder-based skills."""
    raise NotImplementedError


def discover_plugin_skills(project_dir: str = None) -> list[dict]:
    """Read installed_plugins.json and scan plugin skill directories."""
    raise NotImplementedError


def resolve_skill_for_path(
    file_path: str, skill_paths: dict[str, dict] = None
) -> dict | None:
    """Given an absolute file path, return the SkillInfo dict if inside a skill directory."""
    raise NotImplementedError


def classify_file(relative_path: str) -> tuple[str, str]:
    """Classify a file within a skill by type and hierarchy.

    Returns:
        Tuple of (file_type, hierarchy) where:
        - file_type: "markdown" | "script" | "asset" | "reference" | "config"
        - hierarchy: "content" | "script"
    """
    raise NotImplementedError
