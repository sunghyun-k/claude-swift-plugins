---
name: xcstrings-manager
description: iOS .xcstrings 파일의 번역을 추가, 수정, 삭제, 조회하는 스킬. .xcstrings 파일을 직접 읽지 말고 이 스킬 사용.
---

# xcstrings 번역 관리 스킬

iOS xcstrings 파일의 번역을 관리하는 스킬입니다.

## 사전 준비

스크립트 사용 전, 프로젝트에서 `.xcstrings` 파일 위치를 먼저 확인해야 합니다.

## 번역 상태 확인

언어별 번역 완료율을 확인합니다.

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/status.py <xcstrings_path>
```

**옵션:**

- `--json`: JSON 형식으로 출력

**출력 예시:**

```
Total keys: 124
  - Translatable: 123
  - No translate: 1 (APP_STORE)
--------------------------------------------------
ko       [====================] 100.0% (123/123)
en       [====================] 100.0% (123/123)
ja       [====================-]  99.0% (122/123)
```

번역 제외(`shouldTranslate: false`) 키는 통계에서 분리되어 표시됩니다.

## 누락 번역 조회

번역이 누락된 키를 언어별로 조회합니다.

```bash
# 모든 언어의 누락 키 조회
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/list.py <xcstrings_path> --missing

# 특정 언어의 누락 키 조회
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/list.py <xcstrings_path> --missing=ja
```

## 조회

특정 키의 번역을 조회합니다.

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/get.py <xcstrings_path> "KEY_NAME"
```

**옵션:**

- `--lang=LANG`: 특정 언어만 조회 (여러 번 사용 가능)

**예시:**

```bash
# 모든 언어 조회
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/get.py file.xcstrings "BUTTON_SAVE"

# 특정 언어만 조회
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/get.py file.xcstrings "BUTTON_SAVE" --lang=ko --lang=ja
```

## 목록 조회

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/list.py <xcstrings_path>
```

**옵션:**

- `--count`: 개수만 출력
- `--missing`: 누락 번역 조회 (위 섹션 참조)
- `--no-translate`: 번역 제외 키만 조회

## 추가

새 번역 키를 추가합니다. `--ko`, `--en` 또는 `--lang` 옵션 중 최소 하나 필요.

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/add.py <xcstrings_path> "KEY_NAME" [옵션]
```

**옵션:**

- `--ko="값"`: 한국어 번역
- `--en="값"`: 영어 번역
- `--lang=LANG:VALUE`: 추가 언어 (여러 번 사용 가능)
- `--no-translate`: 번역 제외로 마킹 (고유명사 등)

**예시:**

```bash
# 한국어, 영어만 추가
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/add.py file.xcstrings "BUTTON_SAVE" --ko="저장" --en="Save"

# 다국어 일괄 추가
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/add.py file.xcstrings "BUTTON_SAVE" \
  --ko="저장" \
  --en="Save" \
  --lang=ja:保存 \
  --lang=zh-Hans:保存 \
  --lang=fr:Enregistrer

# 번역 제외 (고유명사)
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/add.py file.xcstrings "APP_STORE" --ko="App Store" --no-translate
```

## 수정

기존 키의 번역을 수정합니다.

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update.py <xcstrings_path> "KEY_NAME" [옵션]
```

**옵션:**

- `--ko="값"`: 한국어 번역 수정
- `--en="값"`: 영어 번역 수정
- `--lang=LANG:VALUE`: 추가 언어 수정 (여러 번 사용 가능)
- `--no-translate`: 번역 제외로 마킹
- `--translate`: 번역 제외 해제

**예시:**

```bash
# 한국어만 수정
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update.py file.xcstrings "KEY" --ko="새 한국어"

# 여러 언어 동시 수정
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update.py file.xcstrings "KEY" \
  --ko="한국어" \
  --en="English" \
  --lang=ja:日本語 \
  --lang=zh-Hans:中文

# 번역 제외로 변경
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update.py file.xcstrings "APP_STORE" --no-translate

# 번역 제외 해제
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update.py file.xcstrings "KEY" --translate
```

## 삭제

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/delete.py <xcstrings_path> "KEY_NAME"
```

## 참고

- 키는 UPPER_SNAKE_CASE 사용 (예: `BUTTON_SAVE`, `ERROR_MESSAGE`)
- 지원 언어 코드 예시: `ko`, `en`, `ja`, `zh-Hans`, `zh-Hant`, `fr`, `de`, `es`, `it`, `pt-BR`, `ru`, `ar`, `hi`, `th`, `vi`, `id`, `ms`, `tr`
- 번역 제외 키 (`shouldTranslate: false`): App Store, iPhone 등 고유명사에 사용. 조회 시 `shouldTranslate: false`로 표시됨
