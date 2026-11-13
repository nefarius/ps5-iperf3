#!/usr/bin/env python3
"""Load iperf3.elf on a PS5 ELF loader and relay its standard output."""

import argparse
import http.server
import os
import socket
import sys
import threading
import time
import urllib.parse
from pathlib import Path


def local_ip_toward(host):
    probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        probe.connect((host, 9))
        return probe.getsockname()[0]
    finally:
        probe.close()


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):
        sys.stderr.write("http: " + (fmt % args) + "\n")


def serve(directory):
    handler = lambda *args, **kwargs: QuietHandler(*args, directory=directory, **kwargs)
    server = http.server.ThreadingHTTPServer(("0.0.0.0", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def read_for(sock, seconds):
    sock.settimeout(0.5)
    deadline = time.time() + seconds
    chunks = []
    while time.time() < deadline:
        try:
            data = sock.recv(65536)
        except socket.timeout:
            continue
        if not data:
            break
        chunks.append(data)
        sys.stdout.buffer.write(data)
        sys.stdout.buffer.flush()
    return b"".join(chunks)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--elf", required=True)
    parser.add_argument("--host", default=os.environ.get("PS5_HOST"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("PS5_PORT") or "9021"))
    parser.add_argument("--timeout", type=float, default=25.0)
    parser.add_argument("--http-host", default=os.environ.get("DEPLOY_HTTP_HOST"))
    parser.add_argument("iperf_args", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if args.iperf_args[:1] == ["--"]:
        args.iperf_args = args.iperf_args[1:]
    if not args.host:
        parser.error("set PS5_HOST or pass --host")

    elf = Path(args.elf).resolve()
    httpd = None
    if args.iperf_args:
        httpd = serve(str(elf.parent))
        http_host = args.http_host or local_ip_toward(args.host)
        http_port = httpd.server_address[1]
        quoted = urllib.parse.quote(" ".join(args.iperf_args))
        payload = f"http://{http_host}:{http_port}/{elf.name}?args={quoted}\n".encode()
        sys.stderr.write(payload.decode())
    else:
        payload = elf.read_bytes()
        sys.stderr.write(f"deploy raw {elf}\n")

    sock = socket.create_connection((args.host, args.port), timeout=10)
    try:
        sock.sendall(payload)
        read_for(sock, args.timeout)
    finally:
        sock.close()
        if httpd is not None:
            httpd.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main())
