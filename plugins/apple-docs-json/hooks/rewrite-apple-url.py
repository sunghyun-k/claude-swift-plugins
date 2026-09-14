#!/usr/bin/env python3
"""PreToolUse hook: rewrite Apple Developer doc WebFetch URLs to a machine-readable endpoint.

developer.apple.com docs are a JavaScript-rendered DocC single-page app, so a plain
HTML WebFetch can't read the body.

Rule: /documentation paths serve Markdown when .md is appended.
  https://developer.apple.com/documentation/swiftui/font/resolve(in:)
  -> https://developer.apple.com/documentation/swiftui/font/resolve(in:).md

Rule: /tutorials paths have no .md form, so they keep the DocC data (.json) endpoint.
  https://developer.apple.com/tutorials/swiftui/creating-and-combining-views
  -> https://developer.apple.com/tutorials/data/tutorials/swiftui/creating-and-combining-views.json

Fragments (#...) are dropped and queries (?language=objc) preserved. Non-DocC paths
(videos, forums, design/HIG, ...) and already-rewritten URLs pass through untouched.
"""

import json
import sys
from urllib.parse import urlsplit, urlunsplit


def rewrite(path):
    """Return the rewritten path, or None to leave the URL alone."""
    lower = path.lower()

    # Already rewritten.
    if lower.startswith("/tutorials/data/") or lower.endswith(".md"):
        return None

    if lower.startswith("/documentation"):
        return path.rstrip("/") + ".md"

    if lower.startswith("/tutorials"):
        return "/tutorials/data" + path.rstrip("/") + ".json"

    return None


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    url = input_data.get("tool_input", {}).get("url", "")
    parts = urlsplit(url)

    if parts.netloc.lower() != "developer.apple.com":
        sys.exit(0)

    new_path = rewrite(parts.path)
    if new_path is None:
        sys.exit(0)

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
