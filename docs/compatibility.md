# Compatibility

The ELF is built with PS5 Payload SDK 0.45 and identifies itself as iperf 3.22. Prosper0GDK's Clang target already defines `__FreeBSD__`, so the upstream FreeBSD paths for `sendfile` and `TCP_INFO` are used without a source fork. The control connection and data streams are the upstream iperf3 protocol. Desktop iperf3 3.x peers do not need a PS5-specific client.

## Verified by the in-container checks

- Vendored sources match the published iperf 3.22 archive.
- `build/iperf3.elf` is an ELF64 x86-64 PIE and links the payload kernel library.
- The host reference build accepts `-s`, `-c`, `-u`, `-R`, `-P`, `-J`, and `-i`.

`make check` also runs a one-second TCP transfer between two host iperf 3.22 processes and checks that both JSON reports contain `bits_per_second`.

`make device-check` loads the ELF through an elfldr on `PS5_HOST` port 9021. It covers a no-argument usage launch, PS5 client and server TCP tests, reverse mode, two parallel streams, and a 10 Mbit/s UDP test. JSON output is requested on those runs. Set `PS5_HOST` to the console address before running it.

## Compiled from the SDK surface

These options use interfaces that the SDK headers and libraries export. They are not in the default device-test matrix:

| Option | Status |
| --- | --- |
| `-A` CPU affinity | FreeBSD `cpuset_setaffinity` is linked. Runtime affinity is not part of the smoke test. |
| `-C` TCP congestion | `TCP_CONGESTION` is visible in the SDK headers. |
| `-Z` zero copy | Enabled through the FreeBSD `sendfile` path. |
| `-D` daemon and `--pidfile` | `daemon()` is present. Detaching from the loader socket can end the captured session, so foreground `-s` is the deployment path. |
| `--skip-rx-copy` | `MSG_TRUNC` exists. Its receive behavior is not treated as Linux-compatible. |
| IPv6 | The socket API is compiled in. The device tests use IPv4. |

## Left disabled

OpenSSL authentication, SCTP, MPTCP, UDP GSO/GRO, packet pacing, and bind-to-device are not enabled. The payload SDK does not provide OpenSSL or `sctp_bindx`, and the Linux-only socket options are absent from its headers.

## Socket nonblocking

`patches/0001-ps5-nonblocking-fallback.patch` keeps the normal `fcntl(O_NONBLOCK)` path and falls back to `ioctl(FIONBIO)` when a console socket rejects `F_SETFL`. That fallback is what timed connects use.
