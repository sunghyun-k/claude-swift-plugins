---
name: xcassets-image-manager
description: xcassets 이미지(imageset) 추가/조회/삭제. .imageset/Contents.json을 직접 읽지 말고 이 스킬 사용.
---

# xcassets 이미지 관리 스킬

xcassets 내의 이미지(imageset)를 관리하는 스킬입니다.

## 사전 준비

스크립트 사용 전, 프로젝트에서 `.xcassets` 파일 위치를 먼저 확인해야 합니다.

## 조회

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/list_images.py <xcassets_path>
```

**옵션:**

- `--folder <폴더>`: 특정 폴더만 조회
- `--json`: JSON 형식으로 출력

**예시:**

```bash
# 전체 이미지 목록
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/list_images.py ./Assets.xcassets

# 특정 폴더 조회
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/list_images.py ./Assets.xcassets --folder icons
```

## 추가

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/add_image.py <xcassets_path> <이미지경로> [옵션]
```

**옵션:**

- `--name <이름>`: 이미지셋 이름 (기본: 파일명)
- `--folder <폴더>`: xcassets 내 폴더 경로
- `--scale <1|2|3>`: 이미지 스케일 지정
- `--single-scale`: Single scale 모드 (SVG/PDF 벡터 이미지용)

**예시:**

```bash
# 기본 사용
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/add_image.py ./Assets.xcassets ~/Downloads/icon.png --name appIcon --folder icons

# Single scale 모드 (SVG/PDF 권장)
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/add_image.py ./Assets.xcassets ~/Downloads/icon.svg --single-scale
```

## 삭제

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/delete_image.py <xcassets_path> <이미지셋이름> --force
```

**옵션:**

- `--folder <폴더>`: 이미지셋이 있는 폴더
- `--force`, `-f`: 확인 없이 삭제

## 참고

지원 포맷:

- PNG (권장)
- JPEG/JPG
- PDF (벡터)
- SVG (자동 PDF 변환)

스케일 자동 감지 (파일명 기준):

- `icon.png` → 1x
- `icon@2x.png` → 2x
- `icon@3x.png` → 3x
