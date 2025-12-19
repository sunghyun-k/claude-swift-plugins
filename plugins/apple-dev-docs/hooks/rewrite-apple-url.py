#!/usr/bin/env python3
import json
import sys
import re

try:
    input_data = json.load(sys.stdin)
except json.JSONDecodeError as e:
    print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
    sys.exit(1)

tool_name = input_data.get("tool_name", "")
tool_input = input_data.get("tool_input", {})

# Only process WebFetch calls
if tool_name != "WebFetch":
    sys.exit(0)

url = tool_input.get("url", "")

# Check if URL is from developer.apple.com
if re.search(r"developer\.apple\.com", url, re.IGNORECASE):
    # Replace developer.apple.com with sosumi.ai
    new_url = re.sub(
        r"https?://developer\.apple\.com",
        "https://sosumi.ai",
        url,
        flags=re.IGNORECASE
    )

    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
            "updatedInput": {
                "url": new_url,
                "prompt": tool_input.get("prompt", "")
            }
        }
    }
    print(json.dumps(output))
    sys.exit(0)

# Not an Apple docs URL, proceed normally
sys.exit(0)
