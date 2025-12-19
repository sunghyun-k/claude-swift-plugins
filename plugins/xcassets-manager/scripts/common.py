#!/usr/bin/env python3
"""
xcassets 공통 유틸리티 모듈

colorset, imageset 등 xcassets 에셋 관리에 공통으로 사용되는 함수들
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


def find_xcassets_root(start_path: Optional[str | Path] = None) -> Optional[Path]:
    """프로젝트 내 xcassets 폴더를 찾습니다.

    Args:
        start_path: 검색 시작 경로 (기본: 현재 디렉토리)

    Returns:
        찾은 xcassets 경로, 없으면 None
    """
    if start_path is None:
        start_path = Path.cwd()
    else:
        start_path = Path(start_path).resolve()

    # 직접 지정된 경우
    if start_path.suffix == ".xcassets" and start_path.exists():
        return start_path

    # 하위 디렉토리에서 검색
    for xcassets in start_path.rglob("*.xcassets"):
        if xcassets.is_dir():
            return xcassets

    return None


def find_all_xcassets(start_path: Optional[str | Path] = None) -> list[Path]:
    """모든 xcassets 폴더를 찾습니다.

    Args:
        start_path: 검색 시작 경로 (기본: 현재 디렉토리)

    Returns:
        찾은 모든 xcassets 경로 목록
    """
    if start_path is None:
        start_path = Path.cwd()
    else:
        start_path = Path(start_path).resolve()

    return [p for p in start_path.rglob("*.xcassets") if p.is_dir()]


def create_folder_json(provides_namespace: bool = False) -> dict:
    """xcassets 폴더의 Contents.json을 생성합니다.

    Args:
        provides_namespace: namespace 제공 여부 (기본: False)

    Returns:
        Contents.json 데이터
    """
    data = {
        "info": {
            "author": "xcode",
            "version": 1
        }
    }

    if provides_namespace:
        data["properties"] = {"provides-namespace": True}

    return data


def ensure_folder_exists(xcassets: Path, folder: str) -> Path:
    """xcassets 내 폴더가 존재하는지 확인하고, 없으면 생성합니다.

    Args:
        xcassets: xcassets 경로
        folder: 생성할 폴더 경로 (xcassets 기준 상대 경로)

    Returns:
        생성된/기존 폴더 경로
    """
    target_dir = xcassets / folder

    if not target_dir.exists():
        target_dir.mkdir(parents=True)
        contents_file = target_dir / "Contents.json"
        with open(contents_file, "w", encoding="utf-8") as f:
            json.dump(create_folder_json(), f, indent=2)

    return target_dir


def read_contents_json(path: Path) -> Optional[dict]:
    """Contents.json 파일을 읽습니다.

    Args:
        path: .colorset, .imageset 등의 디렉토리 경로

    Returns:
        파싱된 JSON 데이터, 실패 시 None
    """
    contents_file = path / "Contents.json"
    if not contents_file.exists():
        return None

    try:
        with open(contents_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def write_contents_json(path: Path, data: dict) -> bool:
    """Contents.json 파일을 씁니다.

    Args:
        path: .colorset, .imageset 등의 디렉토리 경로
        data: 저장할 JSON 데이터

    Returns:
        성공 여부
    """
    contents_file = path / "Contents.json"

    try:
        with open(contents_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return True
    except IOError:
        return False


def get_xcassets_path(xcassets_path: Optional[str] = None) -> Optional[Path]:
    """xcassets 경로를 가져옵니다. 지정되지 않으면 자동 탐색합니다.

    Args:
        xcassets_path: 명시적 xcassets 경로 (없으면 자동 탐색)

    Returns:
        xcassets 경로, 찾지 못하면 None
    """
    if xcassets_path:
        xcassets = Path(xcassets_path)
        if xcassets.exists():
            return xcassets
        return None

    return find_xcassets_root()
