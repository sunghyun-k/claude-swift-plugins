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
/plugin install apple-dev-docs@claude-swift-plugins
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

**Supported Tools (auto-detected by config files):**
- Apple swift-format
- nicklockwood/SwiftFormat
- SwiftLint

### apple-dev-docs

Automatically converts `developer.apple.com` URLs to `sosumi.ai` for better Apple documentation access in Claude Code.

### xcstrings-manager

Tools for managing iOS `.xcstrings` localization files.

**Features:**
- Add new localization keys with translations
- Update existing translations
- Delete localization keys
- Query translations for specific keys
- List all keys in an xcstrings file

### xcassets-manager

CRUD management for xcassets resources.

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