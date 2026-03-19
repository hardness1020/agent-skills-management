"""PreToolUse hook entry point.

Reads JSON from stdin, logs skill invocations and nested file accesses,
writes allow response to stdout. Never blocks Claude Code.
"""

import json
import sys


def main() -> None:
    """PreToolUse hook entry point."""
    raise NotImplementedError


if __name__ == "__main__":
    main()
