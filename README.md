# ps5-iperf3

iperf 3.22 as a PS5 homebrew ELF. A desktop iperf3 3.x client measures the path to a console that is running this server.

[![Build](https://github.com/nefarius/ps5-iperf3/actions/workflows/ci.yml/badge.svg)](https://github.com/nefarius/ps5-iperf3/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/github/license/nefarius/ps5-iperf3)](LICENSE)
[![Discord](https://img.shields.io/discord/346756263763378176.svg)](https://discord.nefarius.at/)

## About

The ELF speaks the upstream iperf 3.22 control protocol on port 5201. Build it in Docker with PS5 Payload SDK 0.45, then send it to an [elfldr](https://github.com/ps5-payload-dev/elfldr) already listening on port 9021. The deploy tool writes the ELF and one argument line on that socket. The console does not fetch the payload, and it does not open a connection back to the build machine.

Run the server on the PS5 and the client on a machine that can reach the console. The other direction needs a firewall rule that allows the console to connect to the client.

## Features

- IPv4 TCP and UDP, client and server, on the standard port 5201.
- Reverse mode (`-R`), parallel streams (`-P`), interval reports (`-i`), and JSON output (`-J`).
- Compatible with a desktop iperf3 3.x peer. The check host here is iperf 3.16; the in-container reference build is 3.22.
- Argument passing without a return connection. elfldr leaves the argument line on the payload's standard input.
- Upstream sources stay unmodified in git. PS5 changes are `ps5/` and `patches/`, applied only under `build/`.

## Limitations

- OpenSSL authentication, SCTP, MPTCP, UDP GSO/GRO, packet pacing, and bind-to-device are not compiled in. The SDK has no OpenSSL and no `sctp_bindx`, and those Linux socket options are absent from its headers.
- The default address family is IPv4. `-6` selects IPv6. Device tests use IPv4.
- `-Z` does not use `sendfile`. The payload has no temporary file that `mmap` can use, so the stream buffer is anonymous memory and `-Z` sends with a normal write.
- `-A`, `-C`, `-D`, `--pidfile`, and `--skip-rx-copy` compile against SDK headers. They are not part of the device test.
- `-D` and `--pidfile` detach from the loader socket, which ends the captured session. Use a foreground `-s`.
- `make deploy` reads loader output for 90 seconds. A longer test has to raise that timeout; see [Quick start](#quick-start).
- A PS5 client that connects to the build machine fails unless a firewall rule allows that path. `make device-check` does not cover that direction.
- This is not an iperf 2.x peer.

## Supported systems

| Component | Supported |
| --- | --- |
| Build host | Linux with Docker Engine. The image build was run with Docker 29.9.3 |
| Build image | Ubuntu 24.04, Clang 18, LLD 18, LLVM 18 |
| SDK | [PS5 Payload SDK 0.45](https://github.com/ps5-payload-dev/sdk/releases/tag/v0.45) |
| Console | Jailbroken PS5 with elfldr listening on TCP port 9021 |
| Peer | iperf3 3.x on a host that can open TCP port 5201 to the console |
| Architecture | ELF64 x86-64 PIE |

The console VLAN used for the device test accepts inbound connections from the build host and does not allow the console to connect back.

## Quick start

Prerequisites: Docker, a console at `PS5_HOST` with elfldr on port 9021, and `iperf3` on the machine that will connect in.

```shell
git clone https://github.com/nefarius/ps5-iperf3.git
cd ps5-iperf3
make build
PS5_HOST=ps5.lan make deploy IPERF_ARGS='-s -1'
```

While that command is still attached, from the client machine:

```shell
iperf3 -c ps5.lan -t 1
```

`-s -1` exits after one client. With no `IPERF_ARGS`, the ELF prints iperf3 usage and exits.

`make deploy` closes the loader socket after 90 seconds. For a 15-minute transfer, keep the socket open for the whole run and connect from a second terminal:

```shell
PS5_HOST=ps5.lan python3 tools/ps5_run.py --elf build/iperf3.elf --timeout 1000 -- -s -1
iperf3 -c ps5.lan -t 900
```

`-t 900` is 15 minutes. `--timeout 1000` covers that transfer and the final report. `-i 60` on the client prints one interval per minute.

`make device-check` repeats the short tests: usage, TCP, reverse, two parallel streams, and a 10 Mbit/s UDP test. The desktop client always connects to the PS5. Set `PS5_HOST` first.

## Build

The host Makefile builds `ps5-iperf3-toolchain:3.22` and runs the same targets inside that image when `PS5_PAYLOAD_SDK` is unset. The image downloads SDK 0.45 and checks SHA-256 `5fac64093d0e3e69f2584ce7935f24f703f622d9681f1495c85b9f00d1291a2c`.

Prerequisites:

- Docker Engine with a working `docker build`
- GNU Make
- Python 3, used by `tools/ps5_run.py` on deploy

```shell
make build
make check
```

`make build` writes `build/iperf3.elf`. `make check` verifies the vendored iperf 3.22 archive, checks that the ELF is a 64-bit x86-64 PIE linked to the payload kernel library, builds a host iperf 3.22, and runs a one-second TCP JSON transfer between two host processes.

| Path | Role |
| --- | --- |
| `vendor/iperf-3.22/` | Unmodified iperf 3.22 release |
| `ps5/iperf_config.h` | FreeBSD-compatible feature selection for the SDK |
| `patches/` | Applied to the copy under `build/iperf/` |
| `docker/Dockerfile` | Toolchain image |
| `docs/compatibility.md` | Options that compile and options that stay disabled |

## Continuous integration

Pushes to `master` and pull requests run [`.github/workflows/ci.yml`](.github/workflows/ci.yml) on `ubuntu-latest`. The job runs `make build`, which builds the toolchain image and the ELF inside it, then checks that `build/iperf3.elf` is an ELF64 x86-64 PIE. It does not deploy to a console.

## Support policy

The issue tracker is for defects and concrete changes in this port. Read this README and [docs/compatibility.md](docs/compatibility.md) before opening an issue. A useful report includes the host OS, the desktop iperf3 version, the `PS5_HOST` command, and the loader output.

Issues that ask for jailbreak setup, network redesign, or general iperf usage may be closed. This repository does not provide a jailbreak or iperf help desk.

## Licensing and legal

Files original to this repository are under the [MIT License](LICENSE). Copyright (c) 2026 Benjamin Höglinger-Stelzer. MIT is permissive and can be combined with the BSD-3-Clause iperf sources.

iperf 3.22 stays under its own BSD-3-Clause license, including the U.S. Government license notice in [vendor/iperf-3.22/LICENSE](vendor/iperf-3.22/LICENSE). The MIT grant does not replace that file. Checksums and the SDK license notes are in [THIRD_PARTY.md](THIRD_PARTY.md).

The PS5 Payload SDK is not committed here. Its project files are GPLv3 or later, and the FreeBSD headers it ships are BSD-licensed. The Docker image downloads the pinned archive.

PlayStation and PS5 are trademarks of Sony Interactive Entertainment Inc. This project is not affiliated with Sony.

## Sources and credits

- Upstream iperf: [ESnet iperf 3.22](https://github.com/esnet/iperf), including the bundled [cJSON](https://github.com/DaveGamble/cJSON) 1.7.15 used by the JSON control channel
- Toolchain: [ps5-payload-dev/sdk](https://github.com/ps5-payload-dev/sdk) v0.45 (Prosper0GDK)
- Loader: [ps5-payload-dev/elfldr](https://github.com/ps5-payload-dev/elfldr)
- Build image: Ubuntu 24.04, Clang/LLD/LLVM 18
- Provenance and checksums: [THIRD_PARTY.md](THIRD_PARTY.md)
