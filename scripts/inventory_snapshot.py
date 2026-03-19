"""UserPromptSubmit hook entry point.

Snapshots skill inventory on each conversation start, diffs against
the previous snapshot, and logs skill_added/skill_removed lifecycle
events. Also diffs nested files per skill.
"""

import json
import sys


def main() -> None:
    """UserPromptSubmit hook entry point."""
    raise NotImplementedError


if __name__ == "__main__":
    main()
