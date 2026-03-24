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
/plugin install xcode-mcp-cli@claude-swift-plugins
/plugin install tuist-guard@claude-swift-plugins
/plugin install xcstrings-manager@claude-swift-plugins
/plugin install xcassets-manager@claude-swift-plugins
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

### xcode-mcp-cli

CLI wrapper for Xcode MCP tools (`xcrun mcpbridge`). Provides build, test, diagnostics, preview, code execution, and documentation search via a persistent daemon.

**How it works:**
- Skill: Xcode-specific commands (build, test, preview, diagnostics, docs, etc.)
- Daemon auto-starts on first use; only requires permission approval once

**Features:**
- Build and view build logs
- Run tests (all or specific)
- Render SwiftUI previews
- Get compiler diagnostics for files
- Execute code snippets in project context
- Search Apple Developer Documentation
- Auto-resolves filesystem paths to Xcode project paths

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
