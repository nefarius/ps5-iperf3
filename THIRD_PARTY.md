# Third-party code

Files original to this repository are under the MIT License in [LICENSE](LICENSE). The trees below keep their own licenses.

## iperf 3.22

- Upstream: https://github.com/esnet/iperf
- Source archive: https://downloads.es.net/pub/iperf/iperf-3.22.tar.gz
- SHA-256: `1c0d0fb02c52626111d6e132db80edfbf27bbaff8bd9245df2a371dcb0b35a92`
- Vendored at `vendor/iperf-3.22/` and `vendor/iperf-3.22.tar.gz`
- License: BSD-3-Clause, plus the U.S. Government license notice in `vendor/iperf-3.22/LICENSE`
- The tree is kept unmodified. PS5 changes are the files in `ps5/` and `patches/`, applied only in the ignored `build/` directory.

## PS5 Payload SDK 0.45

- Upstream: https://github.com/ps5-payload-dev/sdk
- Archive: https://github.com/ps5-payload-dev/sdk/releases/download/v0.45/ps5-payload-sdk.zip
- SHA-256: `5fac64093d0e3e69f2584ce7935f24f703f622d9681f1495c85b9f00d1291a2c`
- The Docker image downloads and verifies this archive. It is not committed here.
- SDK license: GPLv3+ for the SDK project files, with BSD-licensed FreeBSD headers under `include/freebsd` as described by the SDK.
