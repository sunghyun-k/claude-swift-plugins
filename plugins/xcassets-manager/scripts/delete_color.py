#!/usr/bin/env python3
from __future__ import annotations
"""
xcassets의 색상을 삭제하는 스크립트

사용법:
    python delete_color.py <xcassets_path> <색상이름> [--folder 폴더] [--force]

예시:
    python delete_color.py ./Assets.xcassets primary
    python delete_color.py ./Assets.xcassets text --folder colors
    python delete_color.py ./Assets.xcassets accent --force
"""

import argparse
import shutil
import sys
from pathlib import Path

# 동일 디렉토리의 모듈 import
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from color_utils import (
    parse_colorset,
    format_color_info,
)


def delete_color(
    xcassets_path: str,
    name: str,
    folder: str | None = None,
    force: bool = False
) -> bool:
    """색상을 삭제합니다."""

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

    # 삭제 전 정보 표시
    color_info = parse_colorset(colorset_path)
    if color_info:
        print("삭제할 색상 정보:")
        print(format_color_info(color_info))
        print()

    # 확인
    if not force:
        confirm = input(f"정말로 '{name}' 색상을 삭제하시겠습니까? (y/N): ")
        if confirm.lower() != "y":
            print("삭제가 취소되었습니다.")
            return False

    # 삭제
    try:
        shutil.rmtree(colorset_path)
        print(f"✓ 색상 삭제 완료: {colorset_path}")
        return True
    except Exception as e:
        print(f"오류: 삭제 실패: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="xcassets의 색상을 삭제합니다.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
    %(prog)s ./Assets.xcassets primary
    %(prog)s ./Assets.xcassets text --folder colors
    %(prog)s ./Assets.xcassets accent --force
        """
    )

    parser.add_argument("xcassets", help="xcassets 폴더 경로")
    parser.add_argument("name", help="삭제할 색상 이름")
    parser.add_argument("--folder", help="검색할 폴더 (xcassets 기준 상대 경로)")
    parser.add_argument("--force", "-f", action="store_true", help="확인 없이 삭제")

    args = parser.parse_args()

    success = delete_color(
        xcassets_path=args.xcassets,
        name=args.name,
        folder=args.folder,
        force=args.force
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
