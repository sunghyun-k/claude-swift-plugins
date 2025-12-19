#!/usr/bin/env python3
from __future__ import annotations
"""
xcassets에 이미지를 추가하는 스크립트

사용법:
    python add_image.py <xcassets_path> <이미지경로> [옵션]

예시:
    python add_image.py ./Assets.xcassets ~/Downloads/icon.png --name appIcon --folder icons
    python add_image.py ./Assets.xcassets ~/Downloads/icon@2x.png --scale 2
"""

import argparse
import json
import shutil
import sys
from pathlib import Path

# 동일 디렉토리의 모듈 import
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from image_utils import (
    parse_scale_from_filename,
    create_imageset_json,
    create_image_entry,
    create_single_scale_image_entry,
    create_empty_image_entry,
    create_folder_json,
)


def add_image(
    xcassets_path: str,
    image_path: str,
    name: str | None = None,
    folder: str | None = None,
    scale: int | None = None,
    single_scale: bool = False,
) -> bool:
    """이미지를 xcassets에 추가합니다."""

    source = Path(image_path)
    if not source.exists():
        print(f"오류: 이미지 파일을 찾을 수 없습니다: {image_path}", file=sys.stderr)
        return False

    # 지원 포맷 확인
    supported_formats = {".png", ".jpg", ".jpeg", ".pdf", ".svg"}
    if source.suffix.lower() not in supported_formats:
        print(f"오류: 지원하지 않는 포맷입니다: {source.suffix}", file=sys.stderr)
        print(f"지원 포맷: {', '.join(supported_formats)}", file=sys.stderr)
        return False

    xcassets = Path(xcassets_path)
    if not xcassets.exists():
        print(f"오류: xcassets 경로를 찾을 수 없습니다: {xcassets_path}", file=sys.stderr)
        return False

    # 이미지셋 이름 결정
    if name:
        imageset_name = name
    else:
        # 파일명에서 @2x 등 제거
        stem = source.stem
        stem = stem.replace("@1x", "").replace("@2x", "").replace("@3x", "")
        imageset_name = stem

    # 스케일 결정
    if scale:
        image_scale = scale
    else:
        image_scale = parse_scale_from_filename(source.name) or 1

    # 대상 경로 결정
    if folder:
        target_dir = xcassets / folder
        # 폴더가 없으면 생성
        if not target_dir.exists():
            target_dir.mkdir(parents=True)
            contents_file = target_dir / "Contents.json"
            with open(contents_file, "w", encoding="utf-8") as f:
                json.dump(create_folder_json(), f, indent=2)
    else:
        target_dir = xcassets

    imageset_dir = target_dir / f"{imageset_name}.imageset"

    # 파일명 생성
    new_filename = f"{imageset_name}{source.suffix}"

    # single scale 모드
    if single_scale:
        if imageset_dir.exists():
            # 기존 파일 모두 삭제
            for f in imageset_dir.iterdir():
                if f.name != "Contents.json":
                    f.unlink()
        else:
            imageset_dir.mkdir(parents=True)

        # 파일 복사
        dest_file = imageset_dir / new_filename
        shutil.copy2(source, dest_file)

        # single scale Contents.json 생성
        images = [create_single_scale_image_entry(new_filename)]
        contents = create_imageset_json(images)
        contents_file = imageset_dir / "Contents.json"
        with open(contents_file, "w", encoding="utf-8") as f:
            json.dump(contents, f, indent=2, ensure_ascii=False)
            f.write("\n")

        print(f"✓ 이미지 추가 완료: {imageset_dir}")
        print(f"  파일: {new_filename}")
        print(f"  모드: single scale")

        return True

    # individual scales 모드
    if imageset_dir.exists():
        # 기존 Contents.json 읽기
        contents_file = imageset_dir / "Contents.json"
        with open(contents_file, encoding="utf-8") as f:
            contents = json.load(f)

        images = contents.get("images", [])

        # 해당 스케일이 이미 있는지 확인
        scale_str = f"{image_scale}x"
        for img in images:
            if img.get("scale") == scale_str and "filename" in img:
                print(f"경고: {scale_str} 스케일 이미지가 이미 존재합니다. 덮어씁니다.")
                # 기존 파일 삭제
                old_file = imageset_dir / img["filename"]
                if old_file.exists():
                    old_file.unlink()
                break
    else:
        # 새 이미지셋 생성
        imageset_dir.mkdir(parents=True)
        images = [
            create_empty_image_entry(1),
            create_empty_image_entry(2),
            create_empty_image_entry(3),
        ]

    # 파일명 생성 (individual scales용)
    if image_scale == 1:
        scale_filename = f"{imageset_name}{source.suffix}"
    else:
        scale_filename = f"{imageset_name}@{image_scale}x{source.suffix}"

    # 파일 복사
    dest_file = imageset_dir / scale_filename
    shutil.copy2(source, dest_file)

    # Contents.json 업데이트
    scale_str = f"{image_scale}x"
    updated = False
    for i, img in enumerate(images):
        if img.get("scale") == scale_str:
            images[i] = create_image_entry(scale_filename, image_scale)
            updated = True
            break

    if not updated:
        images.append(create_image_entry(scale_filename, image_scale))

    # Contents.json 저장
    contents = create_imageset_json(images)
    contents_file = imageset_dir / "Contents.json"
    with open(contents_file, "w", encoding="utf-8") as f:
        json.dump(contents, f, indent=2)

    print(f"✓ 이미지 추가 완료: {imageset_dir}")
    print(f"  파일: {scale_filename}")
    print(f"  스케일: {image_scale}x")

    return True


def main():
    parser = argparse.ArgumentParser(
        description="xcassets에 이미지를 추가합니다.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
    %(prog)s ./Assets.xcassets ~/Downloads/icon.png --name appIcon --folder icons
    %(prog)s ./Assets.xcassets ~/Downloads/icon@2x.png --scale 2
        """,
    )

    parser.add_argument("xcassets", help="xcassets 폴더 경로")
    parser.add_argument("image_path", help="추가할 이미지 파일 경로")
    parser.add_argument("--name", help="이미지셋 이름 (기본: 파일명)")
    parser.add_argument("--folder", help="xcassets 내 폴더 경로")
    parser.add_argument(
        "--scale",
        type=int,
        choices=[1, 2, 3],
        help="이미지 스케일 (1, 2, 3)",
    )
    parser.add_argument(
        "--single-scale",
        action="store_true",
        help="Single scale 모드 (scale 속성 없이 저장)",
    )

    args = parser.parse_args()

    success = add_image(
        args.xcassets,
        args.image_path,
        args.name,
        args.folder,
        args.scale,
        args.single_scale,
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
