---
name: xcode-mcp-cli
description: Xcode MCP 도구 CLI. 빌드, 테스트, 파일 관리, 프리뷰, 진단, 문서 검색 등 Xcode 프로젝트 조작이 필요할 때 사용.
allowed-tools: Bash(python3 *)
---

# Xcode MCP CLI

`xcrun mcpbridge`를 래핑한 CLI 도구. 데몬 방식으로 동작하여 최초 1회만 권한 승인이 필요합니다.

## 기본 사용법

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/xcode_mcp.py <command> [options]
```

**글로벌 옵션:** `--tab ID` (자동 감지), `--pid PID`, `--json` (raw JSON 출력)

## 데몬 관리

데몬은 첫 호출 시 자동 시작됩니다.

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/xcode_mcp.py status
python3 ${CLAUDE_SKILL_DIR}/scripts/xcode_mcp.py stop
```

## 창/탭 조회

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/xcode_mcp.py windows
```

## 파일 관리

```bash
# 디렉토리 목록
python3 ${CLAUDE_SKILL_DIR}/scripts/xcode_mcp.py ls <project-path>

# 파일 검색
python3 ${CLAUDE_SKILL_DIR}/scripts/xcode_mcp.py glob --pattern "*.swift"

# 내용 검색
python3 ${CLAUDE_SKILL_DIR}/scripts/xcode_mcp.py grep "TODO" --type swift
python3 ${CLAUDE_SKILL_DIR}/scripts/xcode_mcp.py grep "pattern" --output content -n -C 3

# 파일 읽기
python3 ${CLAUDE_SKILL_DIR}/scripts/xcode_mcp.py read <file-path>
python3 ${CLAUDE_SKILL_DIR}/scripts/xcode_mcp.py read <file-path> --offset 10 --limit 50

# 파일 쓰기 (인자 또는 stdin)
python3 ${CLAUDE_SKILL_DIR}/scripts/xcode_mcp.py write <file-path> "content"

# 파일 편집 (찾기/바꾸기)
python3 ${CLAUDE_SKILL_DIR}/scripts/xcode_mcp.py edit <file-path> --old "old text" --new "new text"
python3 ${CLAUDE_SKILL_DIR}/scripts/xcode_mcp.py edit <file-path> --old "old" --new "new" --all

# 파일 삭제 / 이동·복사 / 디렉토리 생성
python3 ${CLAUDE_SKILL_DIR}/scripts/xcode_mcp.py rm <path> --recursive
python3 ${CLAUDE_SKILL_DIR}/scripts/xcode_mcp.py mv <source> <dest> [--copy]
python3 ${CLAUDE_SKILL_DIR}/scripts/xcode_mcp.py mkdir <dir-path>
```

## 빌드

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/xcode_mcp.py build
python3 ${CLAUDE_SKILL_DIR}/scripts/xcode_mcp.py build-log --severity warning
```

## 테스트

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/xcode_mcp.py test-list
python3 ${CLAUDE_SKILL_DIR}/scripts/xcode_mcp.py test-all
python3 ${CLAUDE_SKILL_DIR}/scripts/xcode_mcp.py test MyTarget/testMethod
```

## 진단

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/xcode_mcp.py diagnostics <file-path>
python3 ${CLAUDE_SKILL_DIR}/scripts/xcode_mcp.py issues --severity warning
```

## SwiftUI 프리뷰

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/xcode_mcp.py preview <source-file-path>
python3 ${CLAUDE_SKILL_DIR}/scripts/xcode_mcp.py preview <source-file-path> --index 1 --timeout 180
```

## 코드 실행

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/xcode_mcp.py exec <source-file> 'print("hello")'
```

## Apple 문서 검색

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/xcode_mcp.py docs "SwiftUI List"
python3 ${CLAUDE_SKILL_DIR}/scripts/xcode_mcp.py docs "URLSession" --frameworks Foundation
```

## 참고

- 파일 경로는 Xcode 프로젝트 네비게이터 기준 상대 경로 사용
- `glob` 명령으로 프로젝트 내 파일 경로를 먼저 확인 후 사용 권장
- 파일시스템 절대 경로가 아닌 Xcode 프로젝트 구조 경로를 사용
