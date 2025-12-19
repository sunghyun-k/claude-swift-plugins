#!/usr/bin/env python3
from __future__ import annotations
"""
xcassets 내의 이미지 목록을 조회하는 스크립트

사용법:
    python list_images.py <xcassets_path> [--folder 폴더] [--json]

예시:
    python list_images.py ./Assets.xcassets
    python list_images.py ./Assets.xcassets --folder icons
    python list_images.py ./Assets.xcassets --json
"""

import argparse
import json
import sys
from pathlib import Path

# 동일 디렉토리의 모듈 import
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from image_utils import find_imagesets, get_image_info


def list_images(
    xcassets_path: str,
    folder: str | None = None,
) -> list[dict]:
    """이미지 목록을 조회합니다."""

    xcassets = Path(xcassets_path)
    if not xcassets.exists():
        print(f"오류: xcassets 경로를 찾을 수 없습니다: {xcassets_path}", file=sys.stderr)
        return []

    # 검색 경로 결정
    if folder:
        search_path = xcassets / folder
        if not search_path.exists():
            print(f"오류: 폴더를 찾을 수 없습니다: {folder}", file=sys.stderr)
            return []
    else:
        search_path = xcassets

    # 이미지셋 찾기
    imagesets = find_imagesets(search_path)
    results = []

    for imageset in imagesets:
        info = get_image_info(imageset)
        if info:
            # 상대 경로 계산
            try:
                rel_path = imageset.relative_to(xcassets)
                info["relative_path"] = str(rel_path.parent) if rel_path.parent != Path(".") else ""
            except ValueError:
                info["relative_path"] = ""
            results.append(info)

    return results


def main():
    parser = argparse.ArgumentParser(
        description="xcassets 내의 이미지 목록을 조회합니다.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
    %(prog)s ./Assets.xcassets
    %(prog)s ./Assets.xcassets --folder icons
    %(prog)s ./Assets.xcassets --json
        """,
    )

    parser.add_argument("xcassets", help="xcassets 폴더 경로")
    parser.add_argument("--folder", help="조회할 폴더 경로")
    parser.add_argument("--json", action="store_true", help="JSON 형식으로 출력")

    args = parser.parse_args()

    images = list_images(args.xcassets, args.folder)

    if args.json:
        print(json.dumps(images, indent=2, ensure_ascii=False))
    else:
        if not images:
            print("이미지가 없습니다.")
        else:
            print(f"총 {len(images)}개의 이미지:\n")

            # 폴더별로 그룹화
            by_folder: dict[str, list[dict]] = {}
            for img in images:
                folder_key = img["relative_path"] or "(root)"
                if folder_key not in by_folder:
                    by_folder[folder_key] = []
                by_folder[folder_key].append(img)

            for folder_name, folder_images in sorted(by_folder.items()):
                print(f"📁 {folder_name}")
                for img in folder_images:
                    # 스케일 정보
                    if img.get("single_scale"):
                        scales = "single"
                    elif img["scales"]:
                        scales = ", ".join(img["scales"])
                    else:
                        scales = "없음"

                    # 이미지 타입
                    img_type = img.get("image_type", "")
                    type_label = f", {img_type}" if img_type else ""

                    print(f"   • {img['name']} ({scales}{type_label})")
                print()


if __name__ == "__main__":
    main()
