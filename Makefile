ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
IMAGE ?= ps5-iperf3-toolchain:3.22
DOCKER ?= docker

ifeq ($(strip $(PS5_PAYLOAD_SDK)),)

.PHONY: image prepare build clean deploy check device-check

image:
	$(DOCKER) build -t $(IMAGE) -f $(ROOT)/docker/Dockerfile $(ROOT)/docker

prepare build clean deploy check device-check:
	$(MAKE) image
	$(DOCKER) run --rm --network host \
		--user $(shell id -u):$(shell id -g) \
		-v $(ROOT):/src -w /src \
		-e HOME=/tmp \
		-e PS5_PAYLOAD_SDK=/opt/ps5-payload-sdk \
		-e LLVM_CONFIG=/usr/bin/llvm-config-18 \
		-e PS5_HOST \
		-e PS5_PORT \
		-e IPERF_ARGS \
		-e DEPLOY_HTTP_HOST \
		$(IMAGE) $(MAKE) $@

else

include $(PS5_PAYLOAD_SDK)/toolchain/prospero.mk

ELF := build/iperf3.elf
SRC := build/iperf

SRCS := \
	cjson.c \
	dscp.c \
	iperf_api.c \
	iperf_auth.c \
	iperf_client_api.c \
	iperf_error.c \
	iperf_locale.c \
	iperf_pthread.c \
	iperf_sctp.c \
	iperf_server_api.c \
	iperf_tcp.c \
	iperf_time.c \
	iperf_udp.c \
	iperf_util.c \
	main.c \
	net.c \
	tcp_info.c \
	timer.c \
	units.c

CFLAGS += -std=gnu11 -Wall -O2 -g -I$(SRC)

.PHONY: prepare build clean deploy check device-check

prepare:
	rm -rf $(SRC)
	mkdir -p $(SRC)
	cp -a vendor/iperf-3.22/src/. $(SRC)/
	cp ps5/iperf_config.h $(SRC)/iperf_config.h
	cp ps5/version.h $(SRC)/version.h
	set -e; for patch in patches/*.patch; do \
		patch -d $(SRC) -p1 --forward --batch < $$patch; \
	done

$(ELF): prepare
	mkdir -p build
	$(CC) $(CFLAGS) -o $@ $(addprefix $(SRC)/,$(SRCS))

build: $(ELF)

clean:
	rm -rf build

deploy: $(ELF)
	python3 tools/ps5_run.py --elf $(ELF) -- $(IPERF_ARGS)

check: $(ELF)
	tests/check.sh

device-check: $(ELF)
	tests/check.sh --host-only
	tests/device_test.py

endif
