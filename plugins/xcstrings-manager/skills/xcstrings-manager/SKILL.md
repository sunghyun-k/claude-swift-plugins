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

새 번역 키를 추가합니다.

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/add.py <xcstrings_path> "KEY_NAME" --lang=LANG:VALUE [...]
```

**옵션:**

- `--lang=LANG:VALUE`: 언어별 번역 (여러 번 사용 가능)
- `--plural=LANG:CATEGORY:VALUE`: 복수형 variation (여러 번 사용 가능, 아래 복수형 섹션 참조)
- `--json=LANG:JSON`: localization 객체를 JSON으로 직접 지정 (substitutions 등 복합 구조용)
- `--no-translate`: 번역 제외로 마킹 (고유명사 등)

`--lang`, `--plural`, `--json` 중 최소 1개 필수. 같은 언어를 두 옵션에 동시에 줄 수 없음.

**예시:**

```bash
# 한국어, 영어 추가
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/add.py file.xcstrings "BUTTON_SAVE" \
  --lang=ko:저장 --lang=en:Save

# 다국어 일괄 추가
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/add.py file.xcstrings "BUTTON_SAVE" \
  --lang=ko:저장 \
  --lang=en:Save \
  --lang=ja:保存 \
  --lang=zh-Hans:保存

# 번역 제외 (고유명사)
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/add.py file.xcstrings "APP_STORE" \
  --lang=ko:"App Store" --no-translate
```

## 수정

기존 키의 번역을 수정합니다.

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update.py <xcstrings_path> "KEY_NAME" [옵션]
```

**옵션:**

- `--lang=LANG:VALUE`: 언어별 번역 수정 (해당 언어를 단일 stringUnit으로 교체)
- `--plural=LANG:CATEGORY:VALUE`: 복수형 variation 수정. 해당 언어의 기존 plural 카테고리에 **병합**되므로 일부 카테고리만 갱신 가능
- `--json=LANG:JSON`: 해당 언어의 localization 객체 전체를 JSON으로 교체
- `--no-translate`: 번역 제외로 마킹
- `--translate`: 번역 제외 해제

**예시:**

```bash
# 한국어만 수정
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update.py file.xcstrings "KEY" --lang=ko:새한국어

# 여러 언어 동시 수정
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update.py file.xcstrings "KEY" \
  --lang=ko:한국어 \
  --lang=en:English \
  --lang=ja:日本語

# 번역 제외로 변경
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update.py file.xcstrings "APP_STORE" --no-translate

# 번역 제외 해제
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update.py file.xcstrings "KEY" --translate
```

## 복수형 (plural variations)

인자가 1개인 문자열의 복수형은 `--plural=LANG:CATEGORY:VALUE` 로 관리합니다. 카테고리는 CLDR 기준 `zero/one/two/few/many/other` 중 해당 언어에 필요한 것만 채웁니다 (슬라브어: one/few/many/other, 아랍어: 6개 전부, 아시아권 다수: other만 등).

```bash
# 러시아어 복수형 추가 (다른 언어는 --lang과 혼합 가능)
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/add.py file.xcstrings "APP_COUNT" \
  --lang="ko:%lld개 앱" \
  --plural="ru:one:%lld приложение" \
  --plural="ru:few:%lld приложения" \
  --plural="ru:many:%lld приложений" \
  --plural="ru:other:%lld приложений"

# 특정 카테고리만 수정 (기존 카테고리에 병합됨)
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update.py file.xcstrings "APP_COUNT" \
  --plural="ru:zero:0 приложений"
```

인자가 2개 이상이라 인자별 복수형이 필요한 문자열(예: `%1$(covered)lld` + `%2$(total)lld`)은 xcstrings의 `substitutions` 구조가 필요하며, `--json` 으로 localization 객체를 통째로 지정합니다:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update.py file.xcstrings "COVERAGE" --json='en:{
  "stringUnit": {"state": "translated", "value": "Covers %#@covered@ of your %#@total@ apps"},
  "substitutions": {
    "covered": {"argNum": 1, "formatSpecifier": "lld", "variations": {"plural": {
      "one": {"stringUnit": {"state": "translated", "value": "%arg app"}},
      "other": {"stringUnit": {"state": "translated", "value": "%arg apps"}}
    }}},
    "total": {"argNum": 2, "formatSpecifier": "lld", "variations": {"plural": {
      "other": {"stringUnit": {"state": "translated", "value": "%arg"}}
    }}}
  }
}'
```

- 포맷 문자열에서는 각 substitution을 `%#@이름@` 로 참조하고, substitution 내부 값에서는 숫자 자리에 `%arg` 를 사용
- `argNum` 은 Swift 생성 심볼의 argument 순서와 일치해야 함
- `get.py` 는 substitutions 구조를 원본 JSON 그대로 반환

## 삭제

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/delete.py <xcstrings_path> "KEY_NAME"
```

## 참고

- 키는 UPPER_SNAKE_CASE 사용 (예: `BUTTON_SAVE`, `ERROR_MESSAGE`)
- 지원 언어 코드 예시: `ko`, `en`, `ja`, `zh-Hans`, `zh-Hant`, `fr`, `de`, `es`, `it`, `pt-BR`, `ru`, `ar`, `hi`, `th`, `vi`, `id`, `ms`, `tr`
- 번역 제외 키 (`shouldTranslate: false`): App Store, iPhone 등 고유명사에 사용. 조회 시 `shouldTranslate: false`로 표시됨
