#!/usr/bin/env python3
from __future__ import annotations
"""
xcassets 색상 관리를 위한 유틸리티 모듈
"""

import json
import re
import sys
from pathlib import Path
from typing import Optional, TypedDict

# 공통 모듈 import
scripts_dir = Path(__file__).parent.parent.parent.parent / "scripts" / "xcassets"
sys.path.insert(0, str(scripts_dir))

from common import (
    find_xcassets_root,
    find_all_xcassets,
    create_folder_json,
    read_contents_json,
    write_contents_json,
    get_xcassets_path,
)


class ColorComponents(TypedDict, total=False):
    red: str
    green: str
    blue: str
    alpha: str


class ColorData(TypedDict, total=False):
    color_space: str
    components: ColorComponents


class ColorInfo(TypedDict):
    name: str
    path: str
    light: Optional[ColorData]
    dark: Optional[ColorData]


def find_colorsets(xcassets_path: Path) -> list[Path]:
    """xcassets 내의 모든 colorset을 찾습니다."""
    return list(xcassets_path.rglob("*.colorset"))


def find_folders(xcassets_path: Path) -> list[Path]:
    """xcassets 내의 모든 폴더를 찾습니다 (colorset, imageset 등 제외)."""
    folders = []
    for path in xcassets_path.iterdir():
        if path.is_dir() and not path.suffix:
            folders.append(path)
    return folders


def parse_colorset(colorset_path: Path) -> Optional[ColorInfo]:
    """colorset의 Contents.json을 파싱합니다."""
    data = read_contents_json(colorset_path)
    if not data:
        return None

    colors = data.get("colors", [])
    light_color: Optional[ColorData] = None
    dark_color: Optional[ColorData] = None

    for color_entry in colors:
        color_data = color_entry.get("color", {})
        appearances = color_entry.get("appearances", [])

        if not color_data:
            continue

        parsed_color: ColorData = {
            "color_space": color_data.get("color-space", "srgb"),
            "components": color_data.get("components", {})
        }

        is_dark = any(
            a.get("appearance") == "luminosity" and a.get("value") == "dark"
            for a in appearances
        )

        if is_dark:
            dark_color = parsed_color
        else:
            light_color = parsed_color

    return ColorInfo(
        name=colorset_path.stem,
        path=str(colorset_path),
        light=light_color,
        dark=dark_color
    )


def hex_to_components(hex_color: str) -> ColorComponents:
    """HEX 색상을 xcassets 컴포넌트로 변환합니다."""
    hex_color = hex_color.lstrip("#")

    if len(hex_color) == 3:
        hex_color = "".join(c * 2 for c in hex_color)

    if len(hex_color) == 6:
        hex_color += "FF"  # alpha

    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    a = int(hex_color[6:8], 16) / 255.0

    return ColorComponents(
        red=f"{r:.3f}",
        green=f"{g:.3f}",
        blue=f"{b:.3f}",
        alpha=f"{a:.3f}"
    )


def components_to_hex(components: ColorComponents) -> str:
    """xcassets 컴포넌트를 HEX 색상으로 변환합니다."""
    r = int(float(components.get("red", "0")) * 255)
    g = int(float(components.get("green", "0")) * 255)
    b = int(float(components.get("blue", "0")) * 255)
    a = float(components.get("alpha", "1"))

    if a == 1.0:
        return f"#{r:02X}{g:02X}{b:02X}"
    else:
        return f"#{r:02X}{g:02X}{b:02X}{int(a * 255):02X}"


def create_colorset_json(
    light_hex: Optional[str] = None,
    dark_hex: Optional[str] = None,
    color_space: str = "srgb"
) -> dict:
    """colorset Contents.json 데이터를 생성합니다."""
    colors = []

    if light_hex:
        light_components = hex_to_components(light_hex)
        colors.append({
            "color": {
                "color-space": color_space,
                "components": {
                    "alpha": light_components["alpha"],
                    "blue": light_components["blue"],
                    "green": light_components["green"],
                    "red": light_components["red"]
                }
            },
            "idiom": "universal"
        })
    else:
        colors.append({"idiom": "universal"})

    if dark_hex:
        dark_components = hex_to_components(dark_hex)
        colors.append({
            "appearances": [
                {
                    "appearance": "luminosity",
                    "value": "dark"
                }
            ],
            "color": {
                "color-space": color_space,
                "components": {
                    "alpha": dark_components["alpha"],
                    "blue": dark_components["blue"],
                    "green": dark_components["green"],
                    "red": dark_components["red"]
                }
            },
            "idiom": "universal"
        })

    return {
        "colors": colors,
        "info": {
            "author": "xcode",
            "version": 1
        }
    }


def validate_color_name(name: str) -> bool:
    """색상 이름이 유효한지 검사합니다."""
    pattern = r"^[a-zA-Z][a-zA-Z0-9_-]*$"
    return bool(re.match(pattern, name))


def validate_hex_color(hex_color: str) -> bool:
    """HEX 색상이 유효한지 검사합니다."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) not in (3, 6, 8):
        return False
    try:
        int(hex_color, 16)
        return True
    except ValueError:
        return False


def format_color_info(color_info: ColorInfo) -> str:
    """색상 정보를 사람이 읽기 쉬운 형식으로 포맷합니다."""
    lines = [f"색상: {color_info['name']}"]
    lines.append(f"경로: {color_info['path']}")

    if color_info["light"]:
        hex_color = components_to_hex(color_info["light"]["components"])
        lines.append(f"라이트 모드: {hex_color}")
    else:
        lines.append("라이트 모드: (없음)")

    if color_info["dark"]:
        hex_color = components_to_hex(color_info["dark"]["components"])
        lines.append(f"다크 모드: {hex_color}")
    else:
        lines.append("다크 모드: (없음)")

    return "\n".join(lines)


def get_relative_path(colorset_path: Path, xcassets_path: Path) -> str:
    """xcassets 기준 상대 경로를 반환합니다."""
    return str(colorset_path.relative_to(xcassets_path))
