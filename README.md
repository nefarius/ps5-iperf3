# ps5-iperf3

iperf 3.22 as a Prosper0GDK homebrew ELF. The payload speaks the normal iperf3 3.x control protocol, so a desktop `iperf3` client or server can test against the console.

The default listen port remains **5201**. Supported traffic is IPv4 TCP and UDP, in either role, including reverse mode, parallel streams, interval reports, and JSON output.

## Build

Compilation runs in Docker. The image installs Clang 18 and PS5 Payload SDK 0.45; the host only needs Docker.

```bash
make build
make check
```

`make build` produces `build/iperf3.elf`. `make check` confirms the vendored upstream archive, checks that the ELF is a 64-bit x86-64 PIE, and builds a host iperf 3.22 used as the interoperability reference.

## Run on a PS5

The console needs an ELF loader on port 9021, such as [ps5-payload-elfldr](https://github.com/ps5-payload-dev/elfldr). Set `PS5_HOST` to the console address.

A raw deployment has no room for arguments, so it prints iperf3 usage and exits:

```bash
PS5_HOST=192.0.2.10 make deploy
```

To pass a normal iperf3 command line, the loader fetches the ELF over HTTP and receives the arguments in the `args` query parameter:

```bash
PS5_HOST=192.0.2.10 make deploy IPERF_ARGS='-s -1'
PS5_HOST=192.0.2.10 make deploy IPERF_ARGS='-c 192.0.2.1 -t 10'
```

`make device-check` runs the usage launch and TCP, UDP, reverse, and parallel tests against the host reference build. This repository is local-only, so the feature branch is pull-request ready once a Git remote exists.

## Layout

- `vendor/iperf-3.22/` is the unmodified 3.22 release.
- `ps5/iperf_config.h` selects the FreeBSD-compatible features present in the payload SDK.
- `patches/` is applied to a copy under `build/iperf/`.
- `docker/Dockerfile` is the toolchain image.

See [docs/compatibility.md](docs/compatibility.md) for features that are compiled but not part of the verified test set.
