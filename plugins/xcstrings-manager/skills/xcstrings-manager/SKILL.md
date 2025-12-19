---
name: xcstrings-manager
description: iOS .xcstrings 파일의 번역을 추가, 수정, 삭제, 조회하는 스킬. .xcstrings 파일을 직접 읽지 말고 이 스킬 사용.
---

# xcstrings 번역 관리 스킬

iOS xcstrings 파일의 번역을 관리하는 스킬입니다.

## 사전 준비

스크립트 사용 전, 프로젝트에서 `.xcstrings` 파일 위치를 먼저 확인해야 합니다.

## 조회

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/get.py <xcstrings_path> "KEY_NAME"
```

## 목록 조회

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/list.py <xcstrings_path>
```

**옵션:**

- `--count`: 개수만 출력

## 추가

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/add.py <xcstrings_path> "KEY_NAME" --ko="한국어" --en="English"
```

## 수정

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update.py <xcstrings_path> "KEY_NAME" [옵션]
```

**옵션:**

- `--ko="값"`: 한국어 번역 수정
- `--en="값"`: 영어 번역 수정

**예시:**

```bash
# 한국어만 수정
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update.py path/to/file.xcstrings "KEY" --ko="새 한국어"

# 여러 언어 동시 수정
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update.py path/to/file.xcstrings "KEY" --ko="한국어" --en="English"
```

## 삭제

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/delete.py <xcstrings_path> "KEY_NAME"
```

## 참고

- 키는 UPPER_SNAKE_CASE 사용 (예: `BUTTON_SAVE`, `ERROR_MESSAGE`)
