#!/usr/bin/env python3
from __future__ import annotations
"""
xcassets에 새로운 색상을 생성하는 스크립트

사용법:
    python create_color.py <xcassets_path> <색상이름> [--light HEX] [--dark HEX] [--folder 폴더경로]

예시:
    python create_color.py ./Assets.xcassets primary --light "#FF0000" --dark "#00FF00"
    python create_color.py ./Assets.xcassets secondary --light "#0000FF" --folder colors
"""

import argparse
import json
import sys
from pathlib import Path

# 동일 디렉토리의 모듈 import
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from color_utils import (
    create_colorset_json,
    create_folder_json,
    validate_color_name,
    validate_hex_color,
)


def create_color(
    xcassets_path: str,
    name: str,
    light_hex: str | None = None,
    dark_hex: str | None = None,
    folder: str | None = None,
    color_space: str = "srgb"
) -> bool:
    """새로운 색상을 생성합니다."""

    # 색상 이름 유효성 검사
    if not validate_color_name(name):
        print(f"오류: 유효하지 않은 색상 이름입니다: {name}")
        print("색상 이름은 영문자로 시작하고, 영문자/숫자/언더스코어/하이픈만 사용할 수 있습니다.")
        return False

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

    # 대상 경로 결정
    if folder:
        target_dir = xcassets / folder
        # 폴더가 없으면 생성
        if not target_dir.exists():
            target_dir.mkdir(parents=True)
            folder_contents = target_dir / "Contents.json"
            with open(folder_contents, "w", encoding="utf-8") as f:
                json.dump(create_folder_json(), f, indent=2)
            print(f"폴더 생성됨: {folder}")
    else:
        target_dir = xcassets

    # colorset 디렉토리 생성
    colorset_dir = target_dir / f"{name}.colorset"

    if colorset_dir.exists():
        print(f"오류: 색상이 이미 존재합니다: {colorset_dir}")
        return False

    colorset_dir.mkdir(parents=True)

    # Contents.json 생성
    contents_data = create_colorset_json(light_hex, dark_hex, color_space)
    contents_file = colorset_dir / "Contents.json"

    with open(contents_file, "w", encoding="utf-8") as f:
        json.dump(contents_data, f, indent=2)

    print(f"✓ 색상 생성 완료: {colorset_dir}")

    if light_hex:
        print(f"  라이트 모드: {light_hex}")
    if dark_hex:
        print(f"  다크 모드: {dark_hex}")

    return True


def main():
    parser = argparse.ArgumentParser(
        description="xcassets에 새로운 색상을 생성합니다.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
    %(prog)s ./Assets.xcassets primary --light "#FF0000" --dark "#00FF00"
    %(prog)s ./Assets.xcassets secondary --light "#0000FF" --folder colors
        """
    )

    parser.add_argument("xcassets", help="xcassets 폴더 경로")
    parser.add_argument("name", help="생성할 색상 이름")
    parser.add_argument("--light", help="라이트 모드 HEX 색상 (예: #FF0000)")
    parser.add_argument("--dark", help="다크 모드 HEX 색상 (예: #00FF00)")
    parser.add_argument("--folder", help="색상을 생성할 폴더 (xcassets 기준 상대 경로)")
    parser.add_argument("--color-space", default="srgb", help="색상 공간 (기본: srgb)")

    args = parser.parse_args()

    if not args.light and not args.dark:
        print("경고: 색상 값이 지정되지 않았습니다. 빈 색상이 생성됩니다.")

    success = create_color(
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
