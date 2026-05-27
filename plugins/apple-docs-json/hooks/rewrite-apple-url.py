#!/usr/bin/env python3
"""PreToolUse hook: rewrite Apple Developer doc WebFetch URLs to the DocC data (.json) endpoint.

developer.apple.com docs are a JavaScript-rendered DocC single-page app, so a plain
HTML WebFetch can't read the body. The real content is served as JSON from
/tutorials/data/...json, so rewriting the human-facing URL to that data URL returns
the structured source without needing JS.

Rule: for /documentation and /tutorials paths, insert /tutorials/data and append .json.
  https://developer.apple.com/documentation/swiftui/font/resolve(in:)
  -> https://developer.apple.com/tutorials/data/documentation/swiftui/font/resolve(in:).json

Fragments (#...) are dropped and queries (?language=objc) preserved. Non-DocC paths
(videos, forums, design/HIG, ...) and already-data URLs pass through untouched.
"""

import json
import sys
from urllib.parse import urlsplit, urlunsplit


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    url = input_data.get("tool_input", {}).get("url", "")
    parts = urlsplit(url)
    lower = parts.path.lower()

    # Only Apple DocC doc paths. Pass through everything else and already-data URLs.
    if (parts.netloc.lower() != "developer.apple.com"
            or lower.startswith("/tutorials/data/")
            or not lower.startswith(("/documentation", "/tutorials"))):
        sys.exit(0)

    new_path = "/tutorials/data" + parts.path.rstrip("/") + ".json"
    new_url = urlunsplit(("https", parts.netloc, new_path, parts.query, ""))

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
            "updatedInput": {**input_data["tool_input"], "url": new_url},
        }
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
