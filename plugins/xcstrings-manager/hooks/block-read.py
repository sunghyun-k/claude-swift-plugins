#!/usr/bin/env python3
"""PreToolUse hook: Block direct file reads based on JSON rules.

Reads block-rules.json from the same directory.
Exit codes: 0 = allow, 2 = block (stderr message shown)
"""

import fnmatch
import json
import sys
from pathlib import Path


def load_rules() -> list:
    """Load blocking rules from block-rules.json in same directory."""
    rules_path = Path(__file__).parent / "block-rules.json"
    try:
        with open(rules_path, "r") as f:
            data = json.load(f)
            return data.get("rules", [])
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading rules: {e}", file=sys.stderr)
        return []


def main():
    rules = load_rules()
    if not rules:
        sys.exit(0)

    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_name = input_data.get("tool_name", "")
    if tool_name != "Read":
        sys.exit(0)

    file_path = input_data.get("tool_input", {}).get("file_path", "")

    for rule in rules:
        patterns = rule.get("patterns", [])
        message = rule.get("message", "Direct read blocked.")

        for pattern in patterns:
            if fnmatch.fnmatch(file_path, pattern):
                print(f"\u26a0\ufe0f {message}", file=sys.stderr)
                sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
