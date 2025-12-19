#!/usr/bin/env python3
from __future__ import annotations
"""
xcassets 이미지 관리를 위한 유틸리티
"""

import json
import re
import sys
from pathlib import Path

# 공통 모듈 import
scripts_dir = Path(__file__).parent.parent.parent.parent / "scripts" / "xcassets"
sys.path.insert(0, str(scripts_dir))

from common import (
    find_xcassets_root,
    create_folder_json,
    read_contents_json,
    write_contents_json,
    get_xcassets_path,
)


def find_imagesets(folder: Path) -> list[Path]:
    """폴더 내의 모든 imageset을 찾습니다."""
    imagesets = []
    for item in folder.rglob("*.imageset"):
        if item.is_dir():
            imagesets.append(item)
    return sorted(imagesets)


def parse_scale_from_filename(filename: str) -> int | None:
    """파일명에서 스케일을 추출합니다."""
    match = re.search(r"@(\d)x\.", filename)
    if match:
        return int(match.group(1))
    return None


def create_imageset_json(images: list[dict]) -> dict:
    """imageset의 Contents.json을 생성합니다."""
    return {
        "images": images,
        "info": {"author": "xcode", "version": 1},
    }


def create_image_entry(
    filename: str,
    scale: int = 1,
    idiom: str = "universal",
) -> dict:
    """이미지 엔트리를 생성합니다."""
    entry = {
        "filename": filename,
        "idiom": idiom,
        "scale": f"{scale}x",
    }
    return entry


def create_single_scale_image_entry(
    filename: str,
    idiom: str = "universal",
) -> dict:
    """single scale 이미지 엔트리를 생성합니다 (scale 속성 없음)."""
    return {
        "filename": filename,
        "idiom": idiom,
    }


def create_empty_image_entry(scale: int = 1, idiom: str = "universal") -> dict:
    """빈 이미지 엔트리를 생성합니다 (플레이스홀더)."""
    return {
        "idiom": idiom,
        "scale": f"{scale}x",
    }


VECTOR_EXTENSIONS = {".svg", ".pdf"}
BITMAP_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}


def get_image_info(imageset_path: Path) -> dict | None:
    """imageset의 정보를 가져옵니다."""
    data = read_contents_json(imageset_path)
    if not data:
        return None

    images = data.get("images", [])
    scales_present = []
    is_single_scale = False
    image_type = None  # "vector", "bitmap", or None

    for img in images:
        if "filename" in img:
            filename = img["filename"]
            ext = Path(filename).suffix.lower()

            # 이미지 타입 결정
            if ext in VECTOR_EXTENSIONS:
                image_type = "vector"
            elif ext in BITMAP_EXTENSIONS:
                image_type = "bitmap"

            if "scale" in img:
                scales_present.append(img.get("scale"))
            else:
                # scale 속성이 없으면 single scale
                is_single_scale = True

    return {
        "name": imageset_path.stem,
        "path": str(imageset_path),
        "scales": scales_present,
        "image_count": len([i for i in images if "filename" in i]),
        "single_scale": is_single_scale,
        "image_type": image_type,
    }
