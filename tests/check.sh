#!/usr/bin/env bash
# Verify the vendored upstream tree, the PS5 ELF, and a host iperf3 CLI build.
set -euo pipefail

root=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)
cd "$root"

host_only=0
if [[ "${1:-}" == "--host-only" && -x build/host-src/src/iperf3 ]]; then
    host_only=1
fi

echo "1c0d0fb02c52626111d6e132db80edfbf27bbaff8bd9245df2a371dcb0b35a92  vendor/iperf-3.22.tar.gz" | sha256sum -c -

rm -rf build/upstream
mkdir -p build/upstream
tar -xzf vendor/iperf-3.22.tar.gz -C build/upstream
diff -rq build/upstream/iperf-3.22 vendor/iperf-3.22
grep -q FIONBIO build/iperf/net.c

if [[ "$host_only" -eq 0 ]]; then
    header=$(readelf -h build/iperf3.elf)
    dynamic=$(readelf -d build/iperf3.elf)
    payload_strings=$(strings build/iperf3.elf)
    [[ "$header" == *"ELF64"* ]]
    [[ "$header" == *"Advanced Micro Devices X86-64"* ]]
    [[ "$header" == *"DYN"* ]]
    [[ "$dynamic" == *"libkernel"* ]]
    [[ "$payload_strings" == *"iperf 3.22"* ]]
fi

if [[ ! -x build/host-src/src/iperf3 ]]; then
    rm -rf build/host-src
    cp -a vendor/iperf-3.22 build/host-src
    (
        cd build/host-src
        ./configure --without-openssl --disable-shared
        make -j"$(nproc)"
    )
fi

version=$(build/host-src/src/iperf3 -v)
[[ "$version" == *"iperf 3.22"* ]]
help=$(build/host-src/src/iperf3 --help)
for flag in '-s,' '-c,' '-u,' '-R,' '-P,' '-J,' '-i,'; do
    [[ "$help" == *"$flag"* ]]
done

port=15201
build/host-src/src/iperf3 -s -1 -p "$port" -J > build/host-server.json &
server_pid=$!
connected=0
for _ in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20; do
    if build/host-src/src/iperf3 -c 127.0.0.1 -p "$port" -t 1 -J > build/host-client.json; then
        connected=1
        break
    fi
    sleep 0.2
done
wait "$server_pid"
test "$connected" = 1
grep -q bits_per_second build/host-client.json
grep -q bits_per_second build/host-server.json

echo "host and ELF checks passed"
