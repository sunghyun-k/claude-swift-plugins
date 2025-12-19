---
name: xcassets-color-manager
description: xcassets 색상(Color Set) CRUD 및 폴더 관리. .colorset/Contents.json을 직접 읽지 말고 이 스킬 사용.
---

# xcassets 색상 관리 스킬

xcassets의 색상(Color Set)을 관리하는 스킬입니다.

## 사전 준비

스크립트 사용 전, 프로젝트에서 `.xcassets` 파일 위치를 먼저 확인해야 합니다.

## 조회

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/read_color.py <xcassets_path> [색상이름]
```

**옵션:**

- `--folder <폴더>`: 특정 폴더의 색상만 조회
- `--json`: JSON 형식으로 출력

**예시:**

```bash
# 모든 색상 목록
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/read_color.py ./Assets.xcassets

# 특정 색상 상세 정보
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/read_color.py ./Assets.xcassets primary

# 특정 폴더의 색상만 조회
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/read_color.py ./Assets.xcassets --folder colors
```

## 생성

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/create_color.py <xcassets_path> <색상이름> --light "#HEX" --dark "#HEX"
```

**옵션:**

- `--folder <폴더>`: xcassets 내 폴더 경로

**예시:**

```bash
# 기본 생성
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/create_color.py ./Assets.xcassets primary --light "#FF0000" --dark "#00FF00"

# 특정 폴더에 생성
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/create_color.py ./Assets.xcassets primary --light "#FF0000" --dark "#00FF00" --folder colors
```

## 수정

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_color.py <xcassets_path> <색상이름> --light "#새HEX" --dark "#새HEX"
```

**옵션:**

- `--folder <폴더>`: 검색할 폴더

## 삭제

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/delete_color.py <xcassets_path> <색상이름> --force
```

**옵션:**

- `--folder <폴더>`: 검색할 폴더
- `--force`, `-f`: 확인 없이 삭제

## 폴더 관리

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/manage_folder.py <xcassets_path> <명령> [폴더이름]
```

**예시:**

```bash
# 폴더 목록 조회
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/manage_folder.py ./Assets.xcassets list

# 폴더 생성
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/manage_folder.py ./Assets.xcassets create <폴더이름>

# 폴더 삭제
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/manage_folder.py ./Assets.xcassets delete <폴더이름> --force
```

## 참고

HEX 색상 형식:

- `#RGB` (3자리)
- `#RRGGBB` (6자리)
- `#RRGGBBAA` (8자리)
