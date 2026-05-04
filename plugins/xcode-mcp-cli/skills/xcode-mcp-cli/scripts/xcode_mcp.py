#!/usr/bin/env python3
"""xcode-mcp: CLI for Xcode MCP tools via xcrun mcpbridge.

Runs mcpbridge as a persistent daemon to avoid repeated permission prompts.
The daemon auto-starts on first use and communicates via Unix socket.
"""

import argparse
import json
import os
import signal
import socket
import socketserver
import subprocess
import sys
import threading
import time

SOCK_PATH = f"/tmp/xcode-mcp-{os.getuid()}.sock"
PID_PATH = f"/tmp/xcode-mcp-{os.getuid()}.pid"


# ── MCP Bridge (direct mcpbridge communication) ────────────────────────


class MCPError(Exception):
    pass


class MCP:
    """Direct JSON-RPC 2.0 client for xcrun mcpbridge."""

    def __init__(self, pid=None):
        env = os.environ.copy()
        if pid:
            env["MCP_XCODE_PID"] = str(pid)
        self._proc = subprocess.Popen(
            ["xcrun", "mcpbridge"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            env=env,
        )
        self._seq = 0
        self._rpc("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "xcode-mcp-cli", "version": "0.1.0"},
        })
        self._send({"jsonrpc": "2.0", "method": "notifications/initialized"})

    def _send(self, msg):
        self._proc.stdin.write((json.dumps(msg) + "\n").encode())
        self._proc.stdin.flush()

    def _rpc(self, method, params):
        self._seq += 1
        self._send({"jsonrpc": "2.0", "id": self._seq, "method": method, "params": params})
        line = self._proc.stdout.readline()
        if not line:
            raise MCPError("mcpbridge closed unexpectedly")
        resp = json.loads(line)
        if "error" in resp:
            raise MCPError(resp["error"].get("message", str(resp["error"])))
        return resp.get("result", {})

    def tool(self, name, args=None):
        result = self._rpc("tools/call", {"name": name, "arguments": args or {}})
        if result.get("isError"):
            texts = [c["text"] for c in result.get("content", []) if c.get("type") == "text"]
            raise MCPError(f"Tool error: {' '.join(texts)}")
        return result

    def close(self):
        self._proc.stdin.close()
        self._proc.terminate()
        try:
            self._proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            self._proc.kill()


# ── Daemon Server ───────────────────────────────────────────────────────


class DaemonHandler(socketserver.StreamRequestHandler):
    def handle(self):
        try:
            for line in self.rfile:
                if not line.strip():
                    continue
                req = json.loads(line)
                with self.server.lock:
                    try:
                        result = self.server.mcp.tool(req["name"], req.get("arguments"))
                        resp = {"result": result}
                    except MCPError as e:
                        resp = {"error": str(e)}
                self.wfile.write((json.dumps(resp) + "\n").encode())
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, ValueError):
            pass


class DaemonServer(socketserver.ThreadingMixIn, socketserver.UnixStreamServer):
    daemon_threads = True

    def __init__(self, mcp):
        self.mcp = mcp
        self.lock = threading.Lock()
        if os.path.exists(SOCK_PATH):
            os.unlink(SOCK_PATH)
        super().__init__(SOCK_PATH, DaemonHandler)


# ── Remote Client (connects to daemon via socket) ──────────────────────


class RemoteMCP:
    """Client that talks to the daemon over Unix socket."""

    def __init__(self):
        self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._sock.connect(SOCK_PATH)
        self._rfile = self._sock.makefile("r")

    def tool(self, name, args=None):
        msg = json.dumps({"name": name, "arguments": args or {}}) + "\n"
        self._sock.sendall(msg.encode())
        line = self._rfile.readline()
        if not line:
            raise MCPError("daemon connection lost")
        resp = json.loads(line)
        if "error" in resp:
            raise MCPError(resp["error"])
        result = resp["result"]
        if result.get("isError"):
            texts = [c["text"] for c in result.get("content", []) if c.get("type") == "text"]
            raise MCPError(f"Tool error: {' '.join(texts)}")
        return result

    def close(self):
        self._sock.close()


# ── Daemon Lifecycle ────────────────────────────────────────────────────


def daemon_running():
    if not os.path.exists(PID_PATH):
        return False
    try:
        with open(PID_PATH) as f:
            pid = int(f.read().strip())
        os.kill(pid, 0)
        return True
    except (ProcessLookupError, ValueError, PermissionError, FileNotFoundError):
        return False


def start_daemon_bg(xcode_pid=None):
    cmd = [sys.executable, os.path.abspath(__file__)]
    if xcode_pid:
        cmd.extend(["--pid", str(xcode_pid)])
    cmd.append("server")
    subprocess.Popen(
        cmd,
        start_new_session=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
    )


def stop_daemon():
    if os.path.exists(PID_PATH):
        try:
            with open(PID_PATH) as f:
                pid = int(f.read().strip())
            os.kill(pid, signal.SIGTERM)
        except (ProcessLookupError, ValueError, PermissionError):
            pass
        try:
            os.unlink(PID_PATH)
        except FileNotFoundError:
            pass
    if os.path.exists(SOCK_PATH):
        try:
            os.unlink(SOCK_PATH)
        except FileNotFoundError:
            pass


def run_server(xcode_pid=None):
    stop_daemon()
    try:
        mcp = MCP(pid=xcode_pid)
    except (MCPError, OSError, FileNotFoundError) as e:
        # mcpbridge failed to start — exit cleanly so the client retry path
        # observes a missing daemon instead of a stale socket
        sys.stderr.write(f"Failed to start mcpbridge: {e}\n")
        sys.exit(1)
    server = DaemonServer(mcp)

    with open(PID_PATH, "w") as f:
        f.write(str(os.getpid()))

    def cleanup(*_):
        server.shutdown()
        mcp.close()
        for p in (PID_PATH, SOCK_PATH):
            try:
                os.unlink(p)
            except FileNotFoundError:
                pass
        sys.exit(0)

    signal.signal(signal.SIGTERM, cleanup)
    signal.signal(signal.SIGINT, cleanup)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        cleanup()


_DAEMON_STARTUP_ATTEMPTS = 2
_DAEMON_READY_POLL_SECONDS = 0.1
_DAEMON_READY_TIMEOUT_TICKS = 100  # 0.1s × 100 = 10s per attempt


def _connect_or_start(xcode_pid=None, attempts=_DAEMON_STARTUP_ATTEMPTS):
    """Connect to existing daemon or (re)start one. Returns client or None."""
    # Try a healthy existing daemon first
    if daemon_running() and os.path.exists(SOCK_PATH):
        try:
            return RemoteMCP()
        except (ConnectionRefusedError, FileNotFoundError, OSError):
            pass

    # Clean any stale pid/socket before spawning a fresh daemon
    stop_daemon()

    for attempt in range(attempts):
        msg = (
            "Starting MCP daemon..."
            if attempt == 0
            else f"Retrying daemon startup ({attempt + 1}/{attempts})..."
        )
        print(msg, file=sys.stderr)
        start_daemon_bg(xcode_pid)

        for _ in range(_DAEMON_READY_TIMEOUT_TICKS):
            time.sleep(_DAEMON_READY_POLL_SECONDS)
            try:
                return RemoteMCP()
            except (ConnectionRefusedError, FileNotFoundError, OSError):
                # If the daemon process already exited, no point waiting longer
                if not daemon_running() and not os.path.exists(SOCK_PATH):
                    break
                continue

        # Daemon never became ready — clear leftover state before retrying
        stop_daemon()

    return None


def get_client(xcode_pid=None):
    """Get a client, auto-starting daemon if needed."""
    client = _connect_or_start(xcode_pid)
    if client is None:
        sys.exit("Error: could not connect to daemon (is Xcode running?)")
    return client


def _is_daemon_error(e):
    """Check if an MCPError is a daemon connection issue."""
    msg = str(e).lower()
    return "daemon connection lost" in msg or "mcpbridge closed" in msg


_CALL_MAX_RETRIES = 2


def call_with_retry(client, name, args=None, xcode_pid=None, max_retries=_CALL_MAX_RETRIES):
    """Call a tool, restarting the daemon and retrying on connection loss."""
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            return client, client.tool(name, args)
        except MCPError as e:
            if not _is_daemon_error(e):
                raise
            last_error = e
            if attempt >= max_retries:
                break
            print(
                f"Daemon error ({e}). Restarting (attempt {attempt + 1}/{max_retries})...",
                file=sys.stderr,
            )
            try:
                client.close()
            except Exception:
                pass
            stop_daemon()
            client = _connect_or_start(xcode_pid)
            if client is None:
                sys.exit("Error: could not reconnect to daemon (is Xcode running?)")
    raise last_error


# ── Tool Definitions ────────────────────────────────────────────────────
# (cli_cmd, mcp_tool, help, needs_tab, [(cli_arg, mcp_key, argparse_kw)])

S = {"action": "store_true", "default": None}  # shorthand for boolean flags

TOOLS = [
    ("windows", "XcodeListWindows",
     "Lists the current Xcode windows and their workspace information",
     False, []),

    ("build", "BuildProject",
     "Builds an Xcode project and waits until the build completes",
     True, []),

    ("build-log", "GetBuildLog",
     "Gets the log of the current or most recently finished build. Filter by severity, message regex, or file glob",
     True, [
         ("--severity", "severity", {"choices": ["remark", "warning", "error"]}),
         ("--pattern", "pattern", {"help": "regex filter"}),
         ("--glob", "glob", {"help": "file glob filter"}),
     ]),

    ("test-list", "GetTestList",
     "Gets all available tests from the active scheme's active test plan. Results limited to 100; full list written to fullTestListPath",
     True, []),

    ("test-all", "RunAllTests",
     "Runs all tests from the active scheme's active test plan",
     True, []),

    ("test", "RunSomeTests",
     "Runs specific tests using the active scheme's active test plan",
     True, [
         ("tests", "_tests_raw", {"nargs": "+", "metavar": "target/id", "help": "target/identifier pairs"}),
     ]),

    ("diagnostics", "XcodeRefreshCodeIssuesInFile",
     "Retrieves current compiler diagnostics (errors, warnings, notes) for a file",
     True, [
         ("file_path", "filePath", {"help": "source file path"}),
     ]),

    ("issues", "XcodeListNavigatorIssues",
     "Lists the currently known issues in Xcode's Issue Navigator. Filter by severity, regex, or glob",
     True, [
         ("--severity", "severity", {"choices": ["remark", "warning", "error"]}),
         ("--pattern", "pattern", {"help": "regex filter"}),
         ("--glob", "glob", {"help": "file glob filter"}),
     ]),

    ("preview", "RenderPreview",
     "Builds and renders a SwiftUI Preview and returns a snapshot image",
     True, [
         ("file_path", "sourceFilePath", {"help": "source file path"}),
         ("--index", "previewDefinitionIndexInFile", {"type": int, "help": "preview index (0-based)"}),
         ("--timeout", "timeout", {"type": int, "help": "timeout in seconds"}),
     ]),

    ("exec", "ExecuteSnippet",
     "Builds and runs a code snippet in the context of a source file. Output comes from print statements in the snippet",
     True, [
         ("file_path", "sourceFilePath", {"help": "source file for context"}),
         ("snippet", "codeSnippet", {"nargs": "?", "help": "code snippet (stdin if omitted)"}),
     ]),

    ("docs", "DocumentationSearch",
     "Searches Apple Developer Documentation using semantic matching",
     False, [
         ("query", "query", {"help": "search query"}),
         ("--frameworks", "frameworks", {"nargs": "+", "help": "limit to frameworks"}),
     ]),
]


# Path keys that refer to file/directory paths in MCP tools
PATH_KEYS = {"filePath", "sourceFilePath", "path", "sourcePath", "destinationPath", "directoryPath"}


def _glob_once(client, tab, pattern, xcode_pid=None):
    """Run XcodeGlob and return (client, matches)."""
    client, result = call_with_retry(client, "XcodeGlob", {
        "tabIdentifier": tab,
        "pattern": pattern,
    }, xcode_pid=xcode_pid)
    text = ""
    for c in result.get("content", []):
        if c.get("type") == "text":
            text += c["text"]
    data = json.loads(text)
    return client, data.get("matches", [])


def resolve_path(client, tab, path, xcode_pid=None):
    """Try to resolve a filesystem path to an Xcode project path via glob."""
    normalized = path.lstrip("/")
    if not normalized:
        return None

    parts = normalized.split("/")
    candidates = []
    for i in range(len(parts)):
        suffix = "/".join(parts[i:])
        candidates.append(suffix)

    try:
        for suffix in candidates:
            client, matches = _glob_once(client, tab, f"**/{suffix}", xcode_pid=xcode_pid)
            if len(matches) == 1:
                return matches[0]
    except (MCPError, json.JSONDecodeError, KeyError):
        pass
    return None


def build_args(tool_def, parsed, tab):
    """Build MCP tool arguments from parsed CLI args."""
    _, _, _, needs_tab, params = tool_def
    mcp_args = {}
    if needs_tab and tab:
        mcp_args["tabIdentifier"] = tab

    for cli_arg, mcp_key, kw in params:
        if cli_arg.startswith("-"):
            dest = kw.get("dest", cli_arg.lstrip("-").replace("-", "_"))
        else:
            dest = cli_arg

        value = getattr(parsed, dest, None)

        # Stdin fallback for content/snippet params
        if mcp_key in ("content", "codeSnippet") and value is None:
            if sys.stdin.isatty():
                sys.exit(f"Error: provide {mcp_key} as argument or pipe via stdin")
            value = sys.stdin.read()

        # Parse test specifiers: "target/identifier" → {targetName, testIdentifier}
        if mcp_key == "_tests_raw" and value is not None:
            tests = []
            for spec in value:
                parts = spec.split("/", 1)
                if len(parts) != 2:
                    sys.exit(f"Invalid test spec '{spec}': expected 'target/identifier'")
                tests.append({"targetName": parts[0], "testIdentifier": parts[1]})
            mcp_args["tests"] = tests
            continue

        if value is not None:
            mcp_args[mcp_key] = value

    return mcp_args


def print_result(result, raw_json=False):
    """Format and print the MCP tool result."""
    content = result.get("content", [])
    for item in content:
        if item.get("type") == "text":
            text = item["text"]
            if raw_json:
                print(text)
            else:
                try:
                    data = json.loads(text)
                    print(json.dumps(data, indent=2, ensure_ascii=False))
                except (json.JSONDecodeError, TypeError):
                    print(text)
        elif item.get("type") == "image":
            print(f"[Image: {item.get('mimeType', 'unknown')}]")


# ── Main ────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        prog="xcode-mcp",
        description="CLI for Xcode MCP tools (xcrun mcpbridge)",
    )
    parser.add_argument("--pid", type=int, metavar="PID", help="Xcode process ID")
    parser.add_argument("--json", action="store_true", dest="raw_json", help="raw JSON output")

    sub = parser.add_subparsers(dest="command")

    # Register tool subcommands
    tool_map = {}
    for tool_def in TOOLS:
        cmd_name, mcp_tool, help_text, needs_tab, params = tool_def
        sp = sub.add_parser(cmd_name, help=help_text)
        if needs_tab:
            sp.add_argument("--tab", metavar="ID", required=True,
                            help="workspace tab identifier (use 'windows' to find)")
        for cli_arg, mcp_key, kw in params:
            sp.add_argument(cli_arg, **kw)
        tool_map[cmd_name] = tool_def

    # Daemon management subcommands
    sub.add_parser("server", help="Run MCP daemon (internal)")
    sub.add_parser("stop", help="Stop MCP daemon")
    sub.add_parser("status", help="Show daemon status")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    # ── Daemon commands ──
    if args.command == "server":
        run_server(xcode_pid=args.pid)
        return
    if args.command == "stop":
        stop_daemon()
        print("Daemon stopped.")
        return
    if args.command == "status":
        if daemon_running():
            with open(PID_PATH) as f:
                print(f"Daemon running (PID {f.read().strip()})")
        else:
            print("Daemon not running.")
        return

    # ── Tool commands ──
    tool_def = tool_map[args.command]
    _, mcp_tool, _, needs_tab, _ = tool_def

    client = get_client(xcode_pid=args.pid)
    try:
        tab = getattr(args, "tab", None)

        mcp_args = build_args(tool_def, args, tab)
        try:
            client, result = call_with_retry(client, mcp_tool, mcp_args, xcode_pid=args.pid)
        except MCPError as e:
            err_msg = str(e).lower()
            if "not found" not in err_msg:
                raise
            # Try resolving file paths and retry
            resolved_any = False
            for key in PATH_KEYS & mcp_args.keys():
                resolved = resolve_path(client, tab, mcp_args[key], xcode_pid=args.pid)
                if resolved and resolved != mcp_args[key]:
                    mcp_args[key] = resolved
                    resolved_any = True
            if not resolved_any:
                raise
            client, result = call_with_retry(client, mcp_tool, mcp_args, xcode_pid=args.pid)
        print_result(result, raw_json=args.raw_json)
    except MCPError as e:
        sys.exit(f"Error: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    main()
