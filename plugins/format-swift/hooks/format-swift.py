#!/usr/bin/env python3
"""
PostToolUse hook: Edit|Write 후 Swift 파일 자동 포맷팅 및 lint 경고 피드백

지원 도구 (설정 파일 자동 감지):
- Apple swift-format (.swift-format)
- nicklockwood/SwiftFormat (.swiftformat)
- SwiftLint (.swiftlint.yml)
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional


def find_project_root(start_path: str) -> Path:
    """프로젝트 루트 탐색 (CLAUDE_PROJECT_DIR 또는 git root)"""
    if project_dir := os.environ.get("CLAUDE_PROJECT_DIR"):
        return Path(project_dir)

    path = Path(start_path).resolve()
    for parent in [path] + list(path.parents):
        if (parent / ".git").exists():
            return parent
    return path.parent


def detect_tools(project_root: Path) -> list[dict]:
    """설정 파일 기반으로 사용할 도구 감지"""
    tools = []

    # 실행 순서: SwiftLint → SwiftFormat → swift-format
    if (project_root / ".swiftlint.yml").exists():
        tools.append({
            "name": "SwiftLint",
            "format_cmd": ["swiftlint", "--fix", "--format"],
            "lint_cmd": ["swiftlint", "lint", "--quiet"],
        })

    if (project_root / ".swiftformat").exists():
        tools.append({
            "name": "SwiftFormat",
            "format_cmd": ["swiftformat"],
            "lint_cmd": None,  # SwiftFormat에는 별도 lint 명령 없음
        })

    if (project_root / ".swift-format").exists():
        tools.append({
            "name": "swift-format",
            "format_cmd": ["swift-format", "format", "--in-place"],
            "lint_cmd": ["swift-format", "lint"],
        })

    return tools


def run_format(tool: dict, file_path: str) -> None:
    """포맷 명령 실행"""
    try:
        cmd = tool["format_cmd"] + [file_path]
        subprocess.run(cmd, capture_output=True, timeout=30)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass


def run_lint(tool: dict, file_path: str) -> list[str]:
    """lint 명령 실행 후 경고 수집"""
    if not tool.get("lint_cmd"):
        return []

    try:
        cmd = tool["lint_cmd"] + [file_path]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        warnings = []
        output = result.stdout.strip() or result.stderr.strip()
        if output:
            for line in output.split("\n"):
                line = line.strip()
                if line and not line.startswith("Done") and not line.startswith("Linting"):
                    warnings.append(f"[{tool['name']}] {line}")
        return warnings
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []


def output_claude_feedback(warnings: list[str]) -> None:
    """Claude에게 lint 경고 피드백 전달"""
    output = {
        "decision": "block",
        "reason": "Swift lint warnings found:\n" + "\n".join(f"- {w}" for w in warnings),
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": "Consider fixing these lint warnings",
        },
    }
    print(json.dumps(output))


def main() -> None:
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_input = input_data.get("tool_input", {})
    file_path = tool_input.get("file_path") or tool_input.get("filePath") or ""

    if not file_path.endswith(".swift"):
        sys.exit(0)

    if not os.path.exists(file_path):
        sys.exit(0)

    project_root = find_project_root(file_path)
    tools = detect_tools(project_root)

    if not tools:
        sys.exit(0)

    all_warnings: list[str] = []

    for tool in tools:
        run_format(tool, file_path)
        all_warnings.extend(run_lint(tool, file_path))

    if all_warnings:
        output_claude_feedback(all_warnings)

    sys.exit(0)


if __name__ == "__main__":
    main()
