#!/usr/bin/env python3
from __future__ import annotations
"""
xcassets의 폴더를 관리하는 스크립트

사용법:
    python manage_folder.py <xcassets_path> list
    python manage_folder.py <xcassets_path> create <폴더이름> [--parent 부모폴더]
    python manage_folder.py <xcassets_path> delete <폴더이름> [--force]
    python manage_folder.py <xcassets_path> rename <기존이름> <새이름>

예시:
    python manage_folder.py ./Assets.xcassets list
    python manage_folder.py ./Assets.xcassets create colors
    python manage_folder.py ./Assets.xcassets create primary --parent colors
    python manage_folder.py ./Assets.xcassets delete oldColors --force
    python manage_folder.py ./Assets.xcassets rename colors Colors
"""

import argparse
import json
import shutil
import sys
from pathlib import Path

# 동일 디렉토리의 모듈 import
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from color_utils import (
    create_folder_json,
    find_colorsets,
)


def list_folders(xcassets_path: str) -> list[dict]:
    """xcassets 내의 모든 폴더를 조회합니다."""

    xcassets = Path(xcassets_path)
    if not xcassets.exists():
        print(f"오류: xcassets 경로를 찾을 수 없습니다: {xcassets_path}", file=sys.stderr)
        return []

    folders = []

    def scan_folder(path: Path, relative: str = ""):
        for item in sorted(path.iterdir()):
            if item.is_dir():
                # .colorset, .imageset 등 에셋은 제외
                if item.suffix in (".colorset", ".imageset", ".appiconset", ".symbolset"):
                    continue

                folder_relative = f"{relative}/{item.name}" if relative else item.name
                color_count = len(find_colorsets(item))

                folders.append({
                    "name": item.name,
                    "path": folder_relative,
                    "full_path": str(item),
                    "color_count": color_count
                })

                # 재귀적으로 하위 폴더 탐색
                scan_folder(item, folder_relative)

    scan_folder(xcassets)
    return folders


def create_folder(
    xcassets_path: str,
    name: str,
    parent: str | None = None
) -> bool:
    """새 폴더를 생성합니다."""

    xcassets = Path(xcassets_path)
    if not xcassets.exists():
        print(f"오류: xcassets 경로를 찾을 수 없습니다: {xcassets_path}")
        return False

    # 대상 경로 결정
    if parent:
        target_dir = xcassets / parent / name
    else:
        target_dir = xcassets / name

    if target_dir.exists():
        print(f"오류: 폴더가 이미 존재합니다: {target_dir}")
        return False

    # 폴더 생성
    target_dir.mkdir(parents=True)

    # Contents.json 생성
    contents_file = target_dir / "Contents.json"
    with open(contents_file, "w", encoding="utf-8") as f:
        json.dump(create_folder_json(), f, indent=2)

    print(f"✓ 폴더 생성 완료: {target_dir}")
    return True


def delete_folder(
    xcassets_path: str,
    name: str,
    force: bool = False
) -> bool:
    """폴더를 삭제합니다."""

    xcassets = Path(xcassets_path)
    if not xcassets.exists():
        print(f"오류: xcassets 경로를 찾을 수 없습니다: {xcassets_path}")
        return False

    # 폴더 찾기
    target_dir = xcassets / name
    if not target_dir.exists():
        print(f"오류: 폴더를 찾을 수 없습니다: {name}")
        return False

    # 포함된 색상 수 확인
    color_count = len(find_colorsets(target_dir))

    if color_count > 0:
        print(f"경고: 이 폴더에는 {color_count}개의 색상이 포함되어 있습니다.")

    # 확인
    if not force:
        confirm = input(f"정말로 '{name}' 폴더를 삭제하시겠습니까? (y/N): ")
        if confirm.lower() != "y":
            print("삭제가 취소되었습니다.")
            return False

    # 삭제
    try:
        shutil.rmtree(target_dir)
        print(f"✓ 폴더 삭제 완료: {target_dir}")
        return True
    except Exception as e:
        print(f"오류: 삭제 실패: {e}")
        return False


def rename_folder(
    xcassets_path: str,
    old_name: str,
    new_name: str,
) -> bool:
    """폴더 이름을 변경합니다."""

    xcassets = Path(xcassets_path)
    if not xcassets.exists():
        print(f"오류: xcassets 경로를 찾을 수 없습니다: {xcassets_path}")
        return False

    # 기존 폴더 찾기
    old_dir = xcassets / old_name
    if not old_dir.exists():
        print(f"오류: 폴더를 찾을 수 없습니다: {old_name}")
        return False

    # 새 이름 폴더 확인
    new_dir = old_dir.parent / new_name
    if new_dir.exists():
        print(f"오류: 새 이름의 폴더가 이미 존재합니다: {new_name}")
        return False

    # 이름 변경
    try:
        old_dir.rename(new_dir)
        print(f"✓ 폴더 이름 변경 완료: {old_name} -> {new_name}")
        return True
    except Exception as e:
        print(f"오류: 이름 변경 실패: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="xcassets의 폴더를 관리합니다.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
    %(prog)s ./Assets.xcassets list
    %(prog)s ./Assets.xcassets create colors
    %(prog)s ./Assets.xcassets create primary --parent colors
    %(prog)s ./Assets.xcassets delete oldColors --force
    %(prog)s ./Assets.xcassets rename colors Colors
        """
    )

    parser.add_argument("xcassets", help="xcassets 폴더 경로")
    subparsers = parser.add_subparsers(dest="command", help="명령")

    # list 명령
    list_parser = subparsers.add_parser("list", help="폴더 목록 조회")
    list_parser.add_argument("--json", action="store_true", help="JSON 형식으로 출력")

    # create 명령
    create_parser = subparsers.add_parser("create", help="새 폴더 생성")
    create_parser.add_argument("name", help="생성할 폴더 이름")
    create_parser.add_argument("--parent", help="부모 폴더 경로")

    # delete 명령
    delete_parser = subparsers.add_parser("delete", help="폴더 삭제")
    delete_parser.add_argument("name", help="삭제할 폴더 이름")
    delete_parser.add_argument("--force", "-f", action="store_true", help="확인 없이 삭제")

    # rename 명령
    rename_parser = subparsers.add_parser("rename", help="폴더 이름 변경")
    rename_parser.add_argument("old_name", help="기존 폴더 이름")
    rename_parser.add_argument("new_name", help="새 폴더 이름")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "list":
        folders = list_folders(args.xcassets)
        if args.json:
            print(json.dumps(folders, indent=2, ensure_ascii=False))
        else:
            if not folders:
                print("폴더가 없습니다.")
            else:
                print(f"총 {len(folders)}개의 폴더:\n")
                for folder in folders:
                    print(f"  • {folder['path']} ({folder['color_count']}개 색상)")

    elif args.command == "create":
        success = create_folder(args.xcassets, args.name, args.parent)
        sys.exit(0 if success else 1)

    elif args.command == "delete":
        success = delete_folder(args.xcassets, args.name, args.force)
        sys.exit(0 if success else 1)

    elif args.command == "rename":
        success = rename_folder(args.xcassets, args.old_name, args.new_name)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
