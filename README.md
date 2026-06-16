# Claude Swift Plugins

[한국어](README.ko.md)

A Claude Code plugin collection for iOS/Swift development.

> **Note**: Internal instructions (prompts) are written in Korean.

## Installation

### 1. Add the Marketplace

```shell
/plugin marketplace add sunghyun-k/claude-swift-plugins
```

Or using a git URL:

```shell
/plugin marketplace add https://github.com/sunghyun-k/claude-swift-plugins.git
```

### 2. Install Plugins

Install individual plugins:

```shell
/plugin install format-swift@claude-swift-plugins
/plugin install tuist-guard@claude-swift-plugins
/plugin install xcstrings-manager@claude-swift-plugins
/plugin install xcassets-manager@claude-swift-plugins
/plugin install apple-docs-json@claude-swift-plugins
```

Or browse and install interactively:

```shell
/plugin
```

## Plugins

### format-swift

Automatically formats Swift files and reports lint warnings after editing.

**How it works:**
- Hook: `PostToolUse`
- Matcher: `Edit|Write`
- Runs automatically after Swift files are edited/written

**Supported Tools (auto-detected by config files):**
- Apple swift-format
- nicklockwood/SwiftFormat
- SwiftLint

### tuist-guard

Prevents reading/editing Tuist-generated Xcode project files.

**How it works:**
- Hook: `PreToolUse`
- Matcher: `Read|Edit|Write`
- Blocks access to `.xcworkspace` and `.xcodeproj` files and their contents

**When to use:**
- Projects that use Tuist for project generation
- Prevents wasting tokens on generated files that should not be read or modified directly

### xcstrings-manager

Tools for managing iOS `.xcstrings` localization files.

**How it works:**
- Hook: `PreToolUse`
- Matcher: `Read`
- Blocks direct `.xcstrings` file reads, prompting to use the skill instead

**Features:**
- Add new localization keys with translations
- Update existing translations
- Delete localization keys
- Query translations for specific keys
- List all keys in an xcstrings file

### xcassets-manager

CRUD management for xcassets resources.

**How it works:**
- Hook: `PreToolUse`
- Matcher: `Read`
- Blocks direct `.colorset`/`.imageset` file reads, prompting to use the skill instead

**Color Set Features:**
- Create, read, update, delete colors
- Light/Dark mode support
- Folder organization
- HEX color format support (#RGB, #RRGGBB, #RRGGBBAA)

**Image Set Features:**
- Add images with automatic scale detection (@1x, @2x, @3x)
- List and delete imagesets
- Support for PNG, JPEG, PDF, and SVG formats
- Single scale mode for vector images

### apple-docs-json

Rewrites Apple Developer documentation URLs to the DocC data (`.json`) endpoint so WebFetch can read them.

**How it works:**
- Hook: `PreToolUse`
- Matcher: `WebFetch`
- Rewrites `developer.apple.com/documentation/...` (and `/tutorials/...`) URLs to `developer.apple.com/tutorials/data/...json`, returning structured DocC source instead of the JavaScript-rendered page
- Non-documentation Apple URLs (videos, forums, etc.) and non-Apple URLs pass through untouched

**Why:**
- Apple docs are a JS-rendered single-page app, so plain HTML fetches often come back empty
- The `.json` data endpoint is the same source the official site renders, served from Apple's own domain (no third-party proxy)
