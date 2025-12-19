#!/usr/bin/env python3
from __future__ import annotations
"""
xcassets에서 이미지를 삭제하는 스크립트

사용법:
    python delete_image.py <xcassets_path> <이미지셋이름> [옵션]

예시:
    python delete_image.py ./Assets.xcassets oldIcon --folder icons
    python delete_image.py ./Assets.xcassets oldIcon --force
"""

import argparse
import shutil
import sys
from pathlib import Path

# 동일 디렉토리의 모듈 import
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

def delete_image(
    xcassets_path: str,
    name: str,
    folder: str | None = None,
    force: bool = False,
) -> bool:
    """이미지셋을 삭제합니다."""

    xcassets = Path(xcassets_path)
    if not xcassets.exists():
        print(f"오류: xcassets 경로를 찾을 수 없습니다: {xcassets_path}", file=sys.stderr)
        return False

    # 이미지셋 경로 결정
    if folder:
        imageset_dir = xcassets / folder / f"{name}.imageset"
    else:
        # 전체에서 검색
        found = list(xcassets.rglob(f"{name}.imageset"))
        if not found:
            print(f"오류: 이미지셋을 찾을 수 없습니다: {name}", file=sys.stderr)
            return False
        if len(found) > 1:
            print(f"오류: 동일한 이름의 이미지셋이 여러 개 있습니다:", file=sys.stderr)
            for p in found:
                print(f"  - {p.relative_to(xcassets)}", file=sys.stderr)
            print("--folder 옵션으로 경로를 지정해주세요.", file=sys.stderr)
            return False
        imageset_dir = found[0]

    if not imageset_dir.exists():
        print(f"오류: 이미지셋을 찾을 수 없습니다: {imageset_dir}", file=sys.stderr)
        return False

    # 확인
    if not force:
        confirm = input(f"정말로 '{name}' 이미지셋을 삭제하시겠습니까? (y/N): ")
        if confirm.lower() != "y":
            print("삭제가 취소되었습니다.")
            return False

    # 삭제
    try:
        shutil.rmtree(imageset_dir)
        print(f"✓ 이미지셋 삭제 완료: {name}")
        return True
    except Exception as e:
        print(f"오류: 삭제 실패: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="xcassets에서 이미지셋을 삭제합니다.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
    %(prog)s ./Assets.xcassets oldIcon --folder icons
    %(prog)s ./Assets.xcassets oldIcon --force
        """,
    )

    parser.add_argument("xcassets", help="xcassets 폴더 경로")
    parser.add_argument("name", help="삭제할 이미지셋 이름")
    parser.add_argument("--folder", help="이미지셋이 있는 폴더")
    parser.add_argument("--force", "-f", action="store_true", help="확인 없이 삭제")

    args = parser.parse_args()

    success = delete_image(args.xcassets, args.name, args.folder, args.force)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
