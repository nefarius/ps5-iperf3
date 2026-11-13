# ps5-iperf3

iperf 3.22 as a Prosper0GDK homebrew ELF. The payload speaks the normal iperf3 3.x control protocol. Run the server on the console and the client on a desktop that can reach it. The console does not open connections back to the dev machine unless that path is allowed through the firewall.

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

The deploy tool writes the ELF, then one argument line, to the loader socket. elfldr keeps that line on standard input, so the console does not need to open a connection back to the dev machine.

```bash
PS5_HOST=ps5.lan make deploy
PS5_HOST=ps5.lan make deploy IPERF_ARGS='-s -1'
```

With no arguments the ELF prints iperf3 usage and exits. `make deploy` relays loader output for up to 90 seconds, or until the payload closes the socket. While that server is attached, connect from this machine:

```bash
iperf3 -c ps5.lan -t 1
```

`make device-check` loads the ELF through that same socket. The desktop iperf3 connects to the PS5. This repository is local-only, so the feature branch is pull-request ready once a Git remote exists.

## Layout

- `vendor/iperf-3.22/` is the unmodified 3.22 release.
- `ps5/iperf_config.h` selects the FreeBSD-compatible features present in the payload SDK.
- `patches/` is applied to a copy under `build/iperf/`.
- `docker/Dockerfile` is the toolchain image.

See [docs/compatibility.md](docs/compatibility.md) for features that are compiled but not part of the verified test set.
