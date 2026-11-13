#!/usr/bin/env python3
"""Exercise the PS5 ELF against a desktop iperf3.

The console accepts connections from the dev network and does not dial back
out, so every transfer is started by the desktop client.
"""

import os
import socket
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ELF = ROOT / "build" / "iperf3.elf"
HOST_IPERF = ROOT / "build" / "host-src" / "src" / "iperf3"
RUN = ROOT / "tools" / "ps5_run.py"


def run_ps5(args, timeout):
    command = [sys.executable, str(RUN), "--elf", str(ELF), "--timeout", str(timeout), "--"]
    command.extend(args)
    completed = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = completed.stdout + completed.stderr
    if completed.returncode != 0:
        raise RuntimeError(f"ps5 launch failed for {args}: {output}")
    return output


def start_host(binary, args):
    return subprocess.Popen(
        [binary, *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


def wait_for_port(host, port, timeout):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), 0.3):
                return
        except OSError:
            time.sleep(0.2)
    raise TimeoutError(f"{host}:{port} did not accept a connection")


def finish(proc):
    try:
        output, _ = proc.communicate(timeout=20)
    except subprocess.TimeoutExpired:
        proc.kill()
        output, _ = proc.communicate()
    return output or ""


def expect(text, needles, label):
    missing = [needle for needle in needles if needle not in text]
    if missing:
        raise AssertionError(f"{label} missing {missing}\n{text}")


def main():
    ps5 = os.environ.get("PS5_HOST")
    if not ps5:
        raise SystemExit("PS5_HOST is required")
    if not ELF.is_file():
        raise SystemExit("run make build before device tests")
    if not HOST_IPERF.is_file():
        host_iperf = os.environ.get("IPERF3", "iperf3")
    else:
        host_iperf = str(HOST_IPERF)

    port = 5201

    usage = run_ps5([], 15)
    expect(usage, ["Usage", "iperf3"], "usage")

    def ps5_server(extra_client):
        proc = subprocess.Popen(
            [sys.executable, str(RUN), "--elf", str(ELF), "--timeout", "40", "--",
             "-s", "-1", "-p", str(port), "-J"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        client_out = ""
        try:
            wait_for_port(ps5, port, 20)
            client = start_host(host_iperf, ["-c", ps5, "-p", str(port), "-t", "1", "-J", "-i", "1", *extra_client])
            client_out = finish(client)
        finally:
            server_out = finish(proc)
        return client_out + "\n" + server_out

    both = ps5_server([])
    expect(both, ["bits_per_second"], "tcp server")

    both = ps5_server(["-R"])
    expect(both, ["bits_per_second"], "reverse")

    both = ps5_server(["-P", "2"])
    expect(both, ["bits_per_second"], "parallel")

    both = ps5_server(["-u", "-b", "10M"])
    expect(both, ["bits_per_second", "jitter_ms"], "udp")

    print("device checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
