---
name: spi-docs
description: Swift Package Index(swiftpackageindex.com)의 DocC 문서 페이지를 마크다운으로 읽는 스킬. SPI 문서 URL이 주어지거나 Swift 패키지 문서를 읽어야 할 때 사용. 참조 링크도 이어서 접근 가능.
---

# Swift Package Index 문서 → 마크다운

`swiftpackageindex.com` 의 DocC 문서 페이지를 깔끔한 마크다운으로 변환해 읽는 스킬입니다. 변환된 문서의 **Topics / See Also 링크는 모두 다시 이 스킬로 열 수 있는 SPI 문서 URL** 이라, 링크를 따라가며 문서를 탐색할 수 있습니다.

## 언제 쓰나

- `https://swiftpackageindex.com/{owner}/{repo}/{ref}/documentation/...` 형태의 URL 이 주어졌을 때
- "이 Swift 패키지 문서 읽어줘", "GRDB 문서 요약해줘" 등 SPI 문서 열람이 필요할 때

## 왜 브라우저가 필요한가

SPI 는 Cloudflare managed challenge("Just a moment…") 뒤에 있어서 `curl`, `requests`, `WebFetch` 같은 순수 HTTP 클라이언트는 **403** 으로 막힙니다. JS 를 실행하는 실제 브라우저 엔진으로 챌린지를 통과한 뒤, **같은 오리진(same-origin) `fetch`** 로 DocC 데이터 JSON 을 받아야 합니다. 그래서 이 스킬은 세션의 브라우저 도구를 사용합니다.

- 우선순위 1: 인앱 브라우저 — `mcp__Claude_Browser__*` (`javascript_tool`, `preview_start`, `computer`)
- 대안: Chrome 확장 — `mcp__claude-in-chrome__javascript_tool` (동일한 JS 를 실행)

둘 다 없으면 이 스킬은 동작하지 않습니다. 그 경우 사용자에게 브라우저 도구가 필요함을 알리세요.

## 절차

### 1. Cloudflare 통과 (세션당 1회)

브라우저 탭을 아무 SPI 문서 URL 로 엽니다. 이미 `swiftpackageindex.com` 이 열려 있으면 건너뜁니다.

```
preview_start { "url": "<사용자가 준 SPI 문서 URL>" }
```

여는 직후 "잠시만 기다리십시오…"(Cloudflare) 페이지가 뜰 수 있으니 2~3초 대기 후 진행합니다.

```
computer { "action": "wait", "duration": 3 }
```

탭이 실제 문서 제목(예: "GRDB | Documentation")으로 바뀌면 통과된 것입니다.

### 2. 변환기 주입 (탭당 1회)

`${CLAUDE_PLUGIN_ROOT}/skills/spi-docs/docc2md.js` 파일을 Read 로 읽어, 그 **전체 내용을 그대로** 브라우저의 `javascript_tool` 에 `text` 로 실행합니다. 이 스크립트는 `window.__spiDocc` 를 정의합니다.

> 탭을 새로고침하거나 다른 오리진으로 이동하면 `window.__spiDocc` 가 사라지므로 다시 주입합니다. 같은 탭·같은 오리진에 머무는 한 재주입 불필요.

### 3. 페이지 변환

원하는 SPI 문서 URL 로 `convert` 를 호출하고, 반환된 마크다운을 사용자에게 출력합니다.

```js
window.__spiDocc.convert("https://swiftpackageindex.com/groue/GRDB.swift/master/documentation/grdb").then(r => r.markdown)
```

반환값은 `{ url, title, markdown }` 입니다. 보통 `.then(r => r.markdown)` 로 마크다운만 받으면 됩니다.

### 4. 참조 링크 따라가기

출력된 마크다운의 `## Topics` / `## See Also` 링크는 전부 SPI 문서 URL 입니다. 다른 페이지를 읽으려면 그 URL 로 3번(같은 탭이면 주입 없이)만 다시 호출하면 됩니다.

## URL 형태 참고

- 사람용 문서 URL: `.../{owner}/{Repo}/{ref}/documentation/...` (예: `groue/GRDB.swift/master/documentation/grdb`)
- `convert` 는 내부적으로 데이터 엔드포인트 `.../{owner}/{repo-소문자}/{ref}/data/documentation/....json` 를 계산해 fetch 합니다. 사용자에게 보이는 문서 URL 을 그대로 넘기면 됩니다.
- `master`, `main`, 태그, 버전 등 어떤 ref 든 동작합니다.

## 문제 해결

- `HTTP 403` / "Just a moment" → Cloudflare 미통과. 1번을 다시 하고 몇 초 더 대기.
- `__spiDocc is not defined` → 탭이 새로고침됨. 2번(주입) 재실행.
- `Not an SPI documentation URL` → `/documentation/` 이 없는 URL. 올바른 SPI 문서 경로인지 확인.
- 빈/이상한 출력 → 해당 페이지가 문서가 아닐 수 있음(패키지 홈 등). `.../documentation/...` 경로인지 확인.
