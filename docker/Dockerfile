FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
        bash \
        binutils \
        build-essential \
        ca-certificates \
        clang-18 \
        lld-18 \
        llvm-18 \
        make \
        patch \
        python3 \
        socat \
        unzip \
        wget \
    && ln -sf /usr/bin/clang-18 /usr/bin/clang \
    && ln -sf /usr/bin/clang++-18 /usr/bin/clang++ \
    && ln -sf /usr/bin/llvm-config-18 /usr/bin/llvm-config \
    && rm -rf /var/lib/apt/lists/*

ARG SDK_VERSION=v0.45
ARG SDK_SHA256=5fac64093d0e3e69f2584ce7935f24f703f622d9681f1495c85b9f00d1291a2c
RUN wget -O /tmp/ps5-payload-sdk.zip \
        "https://github.com/ps5-payload-dev/sdk/releases/download/${SDK_VERSION}/ps5-payload-sdk.zip" \
    && echo "${SDK_SHA256}  /tmp/ps5-payload-sdk.zip" | sha256sum -c - \
    && unzip -q /tmp/ps5-payload-sdk.zip -d /opt \
    && rm /tmp/ps5-payload-sdk.zip \
    && test -x /opt/ps5-payload-sdk/bin/prospero-clang

ENV PS5_PAYLOAD_SDK=/opt/ps5-payload-sdk
ENV LLVM_CONFIG=/usr/bin/llvm-config-18
ENV PATH="/opt/ps5-payload-sdk/bin:${PATH}"

RUN make -C /opt/ps5-payload-sdk/samples/hello_world

WORKDIR /src
