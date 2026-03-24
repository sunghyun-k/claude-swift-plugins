---
name: xcode-mcp-cli
description: Xcode MCP 도구 CLI. 빌드, 테스트, 프리뷰, 진단, 문서 검색 등 Xcode 프로젝트 조작이 필요할 때 사용.
allowed-tools: Bash(python3 *), Read(//var/folders/**/ActionArtifacts/**)
---

# Xcode MCP CLI

`xcrun mcpbridge`를 래핑한 CLI 도구. 데몬 방식으로 동작하여 최초 1회만 권한 승인이 필요합니다.

파일 관리(읽기, 쓰기, 검색 등)는 시스템 도구(Read, Write, Glob, Grep, Edit, Bash)를 사용하세요. 이 CLI는 Xcode 전용 기능만 제공합니다.

## 기본 사용법

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/xcode_mcp.py <command> [options]
```

**글로벌 옵션:** `--pid PID`, `--json` (raw JSON 출력)
**서브커맨드 옵션:** `--tab ID` (탭 의존 명령에서 필수, `windows`로 확인)

## 워크플로우

대부분의 명령은 `--tab` 옵션이 필요합니다. 먼저 `windows` 명령으로 탭 ID를 확인하세요.

```bash
# 1. 열려있는 Xcode 창/탭 목록 조회
python3 ${CLAUDE_SKILL_DIR}/scripts/xcode_mcp.py windows

# 2. 출력에서 tabIdentifier 확인 후, --tab 옵션으로 사용
python3 ${CLAUDE_SKILL_DIR}/scripts/xcode_mcp.py build --tab <tabIdentifier>
```

탭 ID는 Xcode를 재시작하면 변경됩니다. 명령 실패 시 `windows`로 다시 확인하세요.

파일 경로가 필요한 명령(preview, diagnostics, exec)은 파일시스템 상대 경로를 사용해도 자동으로 Xcode 프로젝트 경로로 변환됩니다.

## 데몬 관리

데몬은 첫 호출 시 자동 시작됩니다.

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/xcode_mcp.py status
python3 ${CLAUDE_SKILL_DIR}/scripts/xcode_mcp.py stop
```

## 빌드

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/xcode_mcp.py build --tab ID
python3 ${CLAUDE_SKILL_DIR}/scripts/xcode_mcp.py build-log --tab ID --severity warning
```

## 테스트

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/xcode_mcp.py test-list --tab ID
python3 ${CLAUDE_SKILL_DIR}/scripts/xcode_mcp.py test-all --tab ID
python3 ${CLAUDE_SKILL_DIR}/scripts/xcode_mcp.py test --tab ID MyTarget/testMethod
```

## 진단

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/xcode_mcp.py diagnostics --tab ID <file-path>
python3 ${CLAUDE_SKILL_DIR}/scripts/xcode_mcp.py issues --tab ID --severity warning
```

## SwiftUI 프리뷰

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/xcode_mcp.py preview --tab ID <source-file-path>
python3 ${CLAUDE_SKILL_DIR}/scripts/xcode_mcp.py preview --tab ID <source-file-path> --index 1 --timeout 180
```

## 코드 실행

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/xcode_mcp.py exec --tab ID <source-file> 'print("hello")'
```

## Apple 문서 검색 (탭 불필요)

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/xcode_mcp.py docs "SwiftUI List"
python3 ${CLAUDE_SKILL_DIR}/scripts/xcode_mcp.py docs "URLSession" --frameworks Foundation
```
