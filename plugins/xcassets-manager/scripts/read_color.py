#!/usr/bin/env python3
from __future__ import annotations
"""
xcassets의 색상을 조회하는 스크립트

사용법:
    python read_color.py <xcassets_path> [색상이름] [--folder 폴더] [--json]

예시:
    python read_color.py ./Assets.xcassets                    # 모든 색상 목록 출력
    python read_color.py ./Assets.xcassets text              # 특정 색상 상세 정보
    python read_color.py ./Assets.xcassets --folder colors   # 특정 폴더의 색상만 조회
    python read_color.py ./Assets.xcassets --json            # JSON 형식으로 출력
"""

import argparse
import json
import sys
from pathlib import Path

# 동일 디렉토리의 모듈 import
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from color_utils import (
    find_colorsets,
    parse_colorset,
    format_color_info,
    get_relative_path,
    components_to_hex,
)


def list_colors(
    xcassets_path: str,
    folder: str | None = None,
) -> list[dict]:
    """모든 색상을 조회합니다."""

    xcassets = Path(xcassets_path)
    if not xcassets.exists():
        print(f"오류: xcassets 경로를 찾을 수 없습니다: {xcassets_path}", file=sys.stderr)
        return []

    # 검색 범위 결정
    if folder:
        search_path = xcassets / folder
        if not search_path.exists():
            print(f"오류: 폴더를 찾을 수 없습니다: {folder}", file=sys.stderr)
            return []
    else:
        search_path = xcassets

    # colorset 찾기
    colorsets = find_colorsets(search_path)
    colors = []

    for colorset in sorted(colorsets):
        color_info = parse_colorset(colorset)
        if color_info:
            color_info["relative_path"] = get_relative_path(colorset, xcassets)
            colors.append(color_info)

    return colors


def get_color(
    xcassets_path: str,
    name: str,
    folder: str | None = None
) -> dict | None:
    """특정 색상을 조회합니다."""

    xcassets = Path(xcassets_path)
    if not xcassets.exists():
        print(f"오류: xcassets 경로를 찾을 수 없습니다: {xcassets_path}", file=sys.stderr)
        return None

    # 검색 범위 결정
    if folder:
        search_path = xcassets / folder
    else:
        search_path = xcassets

    # 색상 찾기
    colorset_name = f"{name}.colorset"
    for colorset in search_path.rglob(colorset_name):
        color_info = parse_colorset(colorset)
        if color_info:
            color_info["relative_path"] = get_relative_path(colorset, xcassets)
            return color_info

    return None


def print_color_list(colors: list[dict], output_json: bool = False):
    """색상 목록을 출력합니다."""
    if output_json:
        # JSON 출력 시 hex 값으로 변환
        output = []
        for color in colors:
            entry = {
                "name": color["name"],
                "path": color["relative_path"],
                "light": None,
                "dark": None
            }
            if color.get("light"):
                entry["light"] = components_to_hex(color["light"]["components"])
            if color.get("dark"):
                entry["dark"] = components_to_hex(color["dark"]["components"])
            output.append(entry)
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        if not colors:
            print("색상이 없습니다.")
            return

        print(f"총 {len(colors)}개의 색상:\n")
        for color in colors:
            light = ""
            dark = ""
            if color.get("light"):
                light = components_to_hex(color["light"]["components"])
            if color.get("dark"):
                dark = components_to_hex(color["dark"]["components"])

            mode_info = []
            if light:
                mode_info.append(f"라이트: {light}")
            if dark:
                mode_info.append(f"다크: {dark}")

            mode_str = ", ".join(mode_info) if mode_info else "(색상 없음)"
            print(f"  • {color['name']} ({color['relative_path']})")
            print(f"    {mode_str}")
            print()


def print_color_detail(color: dict, output_json: bool = False):
    """색상 상세 정보를 출력합니다."""
    if output_json:
        output = {
            "name": color["name"],
            "path": color["relative_path"],
            "light": None,
            "dark": None
        }
        if color.get("light"):
            output["light"] = {
                "hex": components_to_hex(color["light"]["components"]),
                "color_space": color["light"]["color_space"],
                "components": color["light"]["components"]
            }
        if color.get("dark"):
            output["dark"] = {
                "hex": components_to_hex(color["dark"]["components"]),
                "color_space": color["dark"]["color_space"],
                "components": color["dark"]["components"]
            }
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        print(format_color_info(color))


def main():
    parser = argparse.ArgumentParser(
        description="xcassets의 색상을 조회합니다.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
    %(prog)s ./Assets.xcassets                    # 모든 색상 목록 출력
    %(prog)s ./Assets.xcassets text              # 특정 색상 상세 정보
    %(prog)s ./Assets.xcassets --folder colors   # 특정 폴더의 색상만 조회
    %(prog)s ./Assets.xcassets --json            # JSON 형식으로 출력
        """
    )

    parser.add_argument("xcassets", help="xcassets 폴더 경로")
    parser.add_argument("name", nargs="?", help="조회할 색상 이름 (생략 시 전체 목록)")
    parser.add_argument("--folder", help="검색할 폴더 (xcassets 기준 상대 경로)")
    parser.add_argument("--json", action="store_true", help="JSON 형식으로 출력")

    args = parser.parse_args()

    if args.name:
        # 특정 색상 조회
        color = get_color(args.xcassets, args.name, args.folder)
        if color:
            print_color_detail(color, args.json)
        else:
            print(f"오류: 색상을 찾을 수 없습니다: {args.name}", file=sys.stderr)
            sys.exit(1)
    else:
        # 전체 목록 조회
        colors = list_colors(args.xcassets, args.folder)
        print_color_list(colors, args.json)


if __name__ == "__main__":
    main()
