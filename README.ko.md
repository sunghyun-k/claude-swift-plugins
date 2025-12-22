# Claude Swift Plugins

iOS/Swift 개발을 위한 Claude Code 플러그인 모음입니다.

[English](README.md)

## 설치 방법

### 1. 마켓플레이스 추가

```shell
/plugin marketplace add sunghyun-k/claude-swift-plugins
```

또는 git URL 사용:

```shell
/plugin marketplace add https://github.com/sunghyun-k/claude-swift-plugins.git
```

### 2. 플러그인 설치

개별 플러그인 설치:

```shell
/plugin install format-swift@claude-swift-plugins
/plugin install apple-dev-docs@claude-swift-plugins
/plugin install xcstrings-manager@claude-swift-plugins
/plugin install xcassets-manager@claude-swift-plugins
```

또는 대화형으로 탐색 및 설치:

```shell
/plugin
```

## 플러그인

### format-swift

Swift 파일 편집 후 자동으로 포맷팅하고 린트 경고를 보고합니다.

**작동 원리:**
- Hook: `PostToolUse`
- Matcher: `Edit|Write`
- Swift 파일 편집/작성 후 자동 실행

**지원 도구 (설정 파일로 자동 감지):**
- Apple swift-format
- nicklockwood/SwiftFormat
- SwiftLint

### apple-dev-docs

`developer.apple.com` URL을 `sosumi.ai`로 자동 변환하여 Claude Code에서 Apple 문서에 더 잘 접근할 수 있게 합니다.

**작동 원리:**
- Hook: `PreToolUse`
- Matcher: `WebFetch`
- URL 요청 전 Apple 문서 URL 변환

### xcstrings-manager

iOS `.xcstrings` 로컬라이제이션 파일 관리 도구입니다.

**작동 원리:**
- Hook: `PreToolUse`
- Matcher: `Read`
- `.xcstrings` 파일 직접 읽기 차단, 스킬 사용 유도

**기능:**
- 번역과 함께 새 로컬라이제이션 키 추가
- 기존 번역 수정
- 로컬라이제이션 키 삭제
- 특정 키의 번역 조회
- xcstrings 파일의 모든 키 목록 조회

### xcassets-manager

xcassets 리소스 CRUD 관리 도구입니다.

**작동 원리:**
- Hook: `PreToolUse`
- Matcher: `Read`
- `.colorset`/`.imageset` 파일 직접 읽기 차단, 스킬 사용 유도

**Color Set 기능:**
- 색상 생성, 조회, 수정, 삭제
- Light/Dark 모드 지원
- 폴더 구조 관리
- HEX 색상 형식 지원 (#RGB, #RRGGBB, #RRGGBBAA)

**Image Set 기능:**
- 자동 스케일 감지로 이미지 추가 (@1x, @2x, @3x)
- imageset 목록 조회 및 삭제
- PNG, JPEG, PDF, SVG 형식 지원
- 벡터 이미지용 Single scale 모드