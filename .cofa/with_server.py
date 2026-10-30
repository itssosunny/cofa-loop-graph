#!/usr/bin/env python3
"""
with_server.py — Run command with one or more background servers and guaranteed cleanup.
100% Python Standard Library. Pure stdlib process group management and TCP readiness probe.

Usage:
    # Single server
    python3 .cofa/with_server.py --server "python3 app.py" --port 3000 -- pytest tests/

    # Multiple servers
    python3 .cofa/with_server.py \
      --server "cd backend && python3 server.py" --port 8000 \
      --server "cd frontend && npm run dev" --port 3000 \
      -- python3 .cofa/cofa_verify.py --live
"""
from __future__ import annotations

import argparse
import os
import signal
import socket
import subprocess
import sys
import tempfile
import time


def is_server_ready(port: int, host: str = "127.0.0.1", timeout: float = 30.0) -> bool:
    """Poll TCP port until server accepts connection or timeout expires."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.create_connection((host, port), timeout=1.0):
                return True
        except (socket.error, ConnectionRefusedError, OSError):
            time.sleep(0.25)
    return False


def kill_process_group(proc: subprocess.Popen, timeout: float = 5.0) -> None:
    """Cleanly terminate and kill entire process group (prevents zombie node/vite/uvicorn)."""
    try:
        pgid = os.getpgid(proc.pid)
    except (ProcessLookupError, OSError):
        return

    # 1. Send SIGTERM to process group
    try:
        os.killpg(pgid, signal.SIGTERM)
    except (ProcessLookupError, OSError):
        return

    # Wait briefly for graceful shutdown
    start = time.time()
    while time.time() - start < timeout:
        if proc.poll() is not None:
            return
        time.sleep(0.1)

    # 2. Force kill with SIGKILL if still running
    try:
        os.killpg(pgid, signal.SIGKILL)
    except (ProcessLookupError, OSError):
        pass


def main() -> int:
    parser = argparse.ArgumentParser(description="Run command with managed background server(s)")
    parser.add_argument(
        "--server", action="append", dest="servers", required=True, help="Server start command (repeatable)"
    )
    parser.add_argument(
        "--port", action="append", dest="ports", type=int, required=True, help="Server port (must match --server count)"
    )
    parser.add_argument(
        "--host", default="127.0.0.1", help="Host address for readiness probe (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--timeout", type=float, default=30.0, help="Readiness timeout in seconds per server (default: 30.0)"
    )
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Command to run after servers are ready")

    args = parser.parse_args()

    # Strip leading '--' if present
    cmd = args.command
    if cmd and cmd[0] == "--":
        cmd = cmd[1:]

    if not cmd:
        print("[with_server] Error: No command specified to run after server readiness.", file=sys.stderr)
        return 1

    if len(args.servers) != len(args.ports):
        print(
            f"[with_server] Error: Count mismatch: {len(args.servers)} --server vs {len(args.ports)} --port arguments.",
            file=sys.stderr,
        )
        return 1

    servers = [{"cmd": s, "port": p} for s, p in zip(args.servers, args.ports)]
    server_procs: list[tuple[subprocess.Popen, tempfile._TemporaryFileWrapper]] = []

    try:
        for idx, srv in enumerate(servers, start=1):
            print(f"[with_server] Starting server {idx}/{len(servers)} on port {srv['port']}: {srv['cmd']}")
            log_file = tempfile.NamedTemporaryFile(mode="w+", prefix=f"cofa_server_{srv['port']}_", delete=True)
            proc = subprocess.Popen(
                srv["cmd"],
                shell=True,
                start_new_session=True,  # Creates a distinct process group for clean killpg
                stdout=log_file,
                stderr=subprocess.STDOUT,
            )
            server_procs.append((proc, log_file))

            print(f"[with_server] Waiting for TCP port {srv['port']} (timeout {args.timeout}s)...")
            if not is_server_ready(srv["port"], host=args.host, timeout=args.timeout):
                # Server failed to become ready
                log_file.seek(0)
                output = log_file.read()
                print(
                    f"[with_server] Error: Server on port {srv['port']} failed to accept connections within {args.timeout}s.",
                    file=sys.stderr,
                )
                if output:
                    print(f"--- Server Output (last 20 lines) ---\n{os.linesep.join(output.splitlines()[-20:])}", file=sys.stderr)
                return 1

            print(f"[with_server] Server {idx} ready on port {srv['port']}")

        print(f"[with_server] All {len(servers)} servers ready. Running: {' '.join(cmd)}\n")
        sys.stdout.flush()
        sys.stderr.flush()

        res = subprocess.run(cmd)
        return res.returncode

    finally:
        print(f"\n[with_server] Stopping {len(server_procs)} background server(s)...")
        for proc, log_file in server_procs:
            kill_process_group(proc)
            try:
                log_file.close()
            except Exception:
                pass
        print("[with_server] All servers stopped cleanly.")


if __name__ == "__main__":
    sys.exit(main())
