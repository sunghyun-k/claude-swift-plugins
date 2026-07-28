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
/plugin install tuist-guard@claude-swift-plugins
/plugin install xcstrings-manager@claude-swift-plugins
/plugin install xcassets-manager@claude-swift-plugins
/plugin install apple-docs-json@claude-swift-plugins
/plugin install spi-docs@claude-swift-plugins
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

### tuist-guard

Tuist가 생성한 Xcode 프로젝트 파일의 읽기/편집을 차단합니다.

**작동 원리:**
- Hook: `PreToolUse`
- Matcher: `Read|Edit|Write`
- `.xcworkspace` 및 `.xcodeproj` 파일과 내부 파일 접근 차단

**사용 시기:**
- Tuist로 프로젝트를 생성하는 프로젝트에서 사용
- 직접 읽거나 수정하면 안 되는 생성 파일에 토큰 낭비 방지

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

### apple-docs-json

Apple Developer 문서 URL을 DocC 데이터(`.json`) 엔드포인트로 재작성하여 WebFetch가 읽을 수 있게 합니다.

**작동 원리:**
- Hook: `PreToolUse`
- Matcher: `WebFetch`
- `developer.apple.com/documentation/...`(및 `/tutorials/...`) URL을 `developer.apple.com/tutorials/data/...json`으로 재작성하여, JS로 렌더링되는 페이지 대신 구조화된 DocC 원본을 반환
- 문서가 아닌 Apple URL(videos, forums 등)과 비-Apple URL은 손대지 않고 통과

**이유:**
- Apple 문서는 JS로 렌더링되는 단일 페이지 앱이라 일반 HTML 페치는 본문이 비어 오는 경우가 많음
- `.json` 데이터 엔드포인트는 공식 사이트가 렌더링하는 것과 동일한 원본이며, Apple 자체 도메인에서 제공(서드파티 프록시 미경유)

### spi-docs

Swift Package Index(`swiftpackageindex.com`)의 DocC 문서 페이지를 깔끔한 마크다운으로 변환해 읽습니다.

**작동 원리:**
- Skill: SPI 문서 URL 이 주어지거나 Swift 패키지 문서 열람이 필요할 때 활성화
- 세션의 브라우저 도구(인앱 브라우저 `mcp__Claude_Browser__*` 또는 Chrome 확장)로 Cloudflare 챌린지를 통과한 뒤, same-origin `fetch` 로 DocC 데이터 JSON 을 받아 마크다운으로 변환
- 변환된 문서의 **Topics / See Also 링크는 전부 다시 열 수 있는 SPI 문서 URL** 이라 링크를 따라가며 탐색 가능

**이유:**
- SPI 는 Cloudflare managed challenge 뒤에 있어 `curl`·`requests`·`WebFetch` 같은 순수 HTTP 클라이언트는 403 으로 막힘 → JS 를 실행하는 실제 브라우저 엔진이 필요
- DocC render JSON 을 제목·개요·코드·선언부·파라미터·Topics 까지 구조 그대로 마크다운화
