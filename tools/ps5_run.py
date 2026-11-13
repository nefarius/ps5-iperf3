#!/usr/bin/env python3
"""Load iperf3.elf on a PS5 ELF loader and relay its standard output.

The console only accepts inbound connections from the dev network. The ELF
bytes and one argument line are written to the loader socket; elfldr leaves
that line on stdin for the payload.
"""

import argparse
import os
import socket
import sys
import time
from pathlib import Path


def quote_arg(arg):
    if arg and not any(ch in arg for ch in " \t\r\n\\\"'"):
        return arg
    escaped = arg.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def read_for(sock, seconds):
    sock.settimeout(0.5)
    deadline = time.time() + seconds
    while time.time() < deadline:
        try:
            data = sock.recv(65536)
        except socket.timeout:
            continue
        if not data:
            break
        sys.stdout.buffer.write(data)
        sys.stdout.buffer.flush()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--elf", required=True)
    parser.add_argument("--host", default=os.environ.get("PS5_HOST"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("PS5_PORT") or "9021"))
    parser.add_argument("--timeout", type=float, default=90.0)
    parser.add_argument("iperf_args", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if args.iperf_args[:1] == ["--"]:
        args.iperf_args = args.iperf_args[1:]
    if not args.host:
        parser.error("set PS5_HOST or pass --host")

    elf = Path(args.elf).resolve()
    payload = elf.read_bytes()
    if args.iperf_args:
        payload += (" ".join(quote_arg(arg) for arg in args.iperf_args) + "\n").encode()
        sys.stderr.write(f"deploy {elf.name} {' '.join(args.iperf_args)} -> {args.host}:{args.port}\n")
    else:
        sys.stderr.write(f"deploy {elf.name} -> {args.host}:{args.port}\n")

    sock = socket.create_connection((args.host, args.port), timeout=10)
    try:
        sock.sendall(payload)
        read_for(sock, args.timeout)
    finally:
        sock.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
