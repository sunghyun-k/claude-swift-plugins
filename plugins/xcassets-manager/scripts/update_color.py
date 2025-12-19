#!/usr/bin/env python3
from __future__ import annotations
"""
xcassets의 기존 색상을 수정하는 스크립트

사용법:
    python update_color.py <xcassets_path> <색상이름> [--light HEX] [--dark HEX] [--folder 폴더]

예시:
    python update_color.py ./Assets.xcassets primary --light "#FF0000"
    python update_color.py ./Assets.xcassets text --dark "#FFFFFF" --folder colors
    python update_color.py ./Assets.xcassets accent --light "#FFCC00" --dark "#FFDD00"
"""

import argparse
import json
import sys
from pathlib import Path

# 동일 디렉토리의 모듈 import
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from color_utils import (
    parse_colorset,
    hex_to_components,
    validate_hex_color,
    components_to_hex,
)


def update_color(
    xcassets_path: str,
    name: str,
    light_hex: str | None = None,
    dark_hex: str | None = None,
    folder: str | None = None,
    color_space: str | None = None
) -> bool:
    """기존 색상을 수정합니다."""

    # HEX 색상 유효성 검사
    if light_hex and not validate_hex_color(light_hex):
        print(f"오류: 유효하지 않은 라이트 모드 색상입니다: {light_hex}")
        return False

    if dark_hex and not validate_hex_color(dark_hex):
        print(f"오류: 유효하지 않은 다크 모드 색상입니다: {dark_hex}")
        return False

    xcassets = Path(xcassets_path)
    if not xcassets.exists():
        print(f"오류: xcassets 경로를 찾을 수 없습니다: {xcassets_path}")
        return False

    # 색상 찾기
    search_path = xcassets / folder if folder else xcassets
    colorset_name = f"{name}.colorset"
    colorset_path = None

    for path in search_path.rglob(colorset_name):
        colorset_path = path
        break

    if not colorset_path:
        print(f"오류: 색상을 찾을 수 없습니다: {name}")
        return False

    # 기존 색상 정보 로드
    contents_file = colorset_path / "Contents.json"
    try:
        with open(contents_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"오류: Contents.json을 읽을 수 없습니다: {e}")
        return False

    # 기존 값 출력
    existing_info = parse_colorset(colorset_path)
    if existing_info:
        print("기존 색상 정보:")
        if existing_info.get("light"):
            print(f"  라이트 모드: {components_to_hex(existing_info['light']['components'])}")
        if existing_info.get("dark"):
            print(f"  다크 모드: {components_to_hex(existing_info['dark']['components'])}")
        print()

    colors = data.get("colors", [])

    # 라이트 모드 색상 업데이트
    if light_hex:
        light_components = hex_to_components(light_hex)
        light_found = False

        for color_entry in colors:
            appearances = color_entry.get("appearances", [])
            is_dark = any(
                a.get("appearance") == "luminosity" and a.get("value") == "dark"
                for a in appearances
            )

            if not is_dark:
                cs = color_space or color_entry.get("color", {}).get("color-space", "srgb")
                color_entry["color"] = {
                    "color-space": cs,
                    "components": {
                        "alpha": light_components["alpha"],
                        "blue": light_components["blue"],
                        "green": light_components["green"],
                        "red": light_components["red"]
                    }
                }
                light_found = True
                break

        # 라이트 모드 색상이 없으면 추가
        if not light_found:
            cs = color_space or "srgb"
            # 빈 universal 엔트리가 있으면 업데이트
            for i, color_entry in enumerate(colors):
                if color_entry.get("idiom") == "universal" and "color" not in color_entry:
                    colors[i] = {
                        "color": {
                            "color-space": cs,
                            "components": {
                                "alpha": light_components["alpha"],
                                "blue": light_components["blue"],
                                "green": light_components["green"],
                                "red": light_components["red"]
                            }
                        },
                        "idiom": "universal"
                    }
                    light_found = True
                    break

            if not light_found:
                colors.insert(0, {
                    "color": {
                        "color-space": cs,
                        "components": {
                            "alpha": light_components["alpha"],
                            "blue": light_components["blue"],
                            "green": light_components["green"],
                            "red": light_components["red"]
                        }
                    },
                    "idiom": "universal"
                })

    # 다크 모드 색상 업데이트
    if dark_hex:
        dark_components = hex_to_components(dark_hex)
        dark_found = False

        for color_entry in colors:
            appearances = color_entry.get("appearances", [])
            is_dark = any(
                a.get("appearance") == "luminosity" and a.get("value") == "dark"
                for a in appearances
            )

            if is_dark:
                cs = color_space or color_entry.get("color", {}).get("color-space", "srgb")
                color_entry["color"] = {
                    "color-space": cs,
                    "components": {
                        "alpha": dark_components["alpha"],
                        "blue": dark_components["blue"],
                        "green": dark_components["green"],
                        "red": dark_components["red"]
                    }
                }
                dark_found = True
                break

        # 다크 모드 색상이 없으면 추가
        if not dark_found:
            cs = color_space or "srgb"
            colors.append({
                "appearances": [
                    {
                        "appearance": "luminosity",
                        "value": "dark"
                    }
                ],
                "color": {
                    "color-space": cs,
                    "components": {
                        "alpha": dark_components["alpha"],
                        "blue": dark_components["blue"],
                        "green": dark_components["green"],
                        "red": dark_components["red"]
                    }
                },
                "idiom": "universal"
            })

    data["colors"] = colors

    # 파일 저장
    with open(contents_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"✓ 색상 수정 완료: {colorset_path}")
    print("변경된 값:")
    if light_hex:
        print(f"  라이트 모드: {light_hex}")
    if dark_hex:
        print(f"  다크 모드: {dark_hex}")

    return True


def main():
    parser = argparse.ArgumentParser(
        description="xcassets의 기존 색상을 수정합니다.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
    %(prog)s ./Assets.xcassets primary --light "#FF0000"
    %(prog)s ./Assets.xcassets text --dark "#FFFFFF" --folder colors
    %(prog)s ./Assets.xcassets accent --light "#FFCC00" --dark "#FFDD00"
        """
    )

    parser.add_argument("xcassets", help="xcassets 폴더 경로")
    parser.add_argument("name", help="수정할 색상 이름")
    parser.add_argument("--light", help="새로운 라이트 모드 HEX 색상")
    parser.add_argument("--dark", help="새로운 다크 모드 HEX 색상")
    parser.add_argument("--folder", help="검색할 폴더 (xcassets 기준 상대 경로)")
    parser.add_argument("--color-space", help="색상 공간 (변경 시에만 지정)")

    args = parser.parse_args()

    if not args.light and not args.dark:
        print("오류: --light 또는 --dark 옵션 중 하나 이상을 지정해야 합니다.")
        sys.exit(1)

    success = update_color(
        xcassets_path=args.xcassets,
        name=args.name,
        light_hex=args.light,
        dark_hex=args.dark,
        folder=args.folder,
        color_space=args.color_space
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
