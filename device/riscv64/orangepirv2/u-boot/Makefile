CROSS_COMPILE := riscv64-linux-gnu-
JOBS := $(shell nproc)
BRANCH := v2022.10-k1-v2.1
REPO := https://github.com/BPI-SINOVOIP/pi-u-boot.git
SRC_DIR := u-boot-orangepi

OPENSBI_REPO := https://github.com/BPI-SINOVOIP/pi-opensbi.git
OPENSBI_BRANCH := v1.3-k1-v2.1
OPENSBI_DIR := pi-opensbi
OPENSBI_BLOB := $(shell pwd)/$(OPENSBI_DIR)/build/platform/generic/firmware/fw_dynamic.bin

default: clone-opensbi build

setup:
	sudo dnf install -y gcc-riscv64-linux-gnu binutils-riscv64-linux-gnu

clone:
	@if [ -d "$(SRC_DIR)" ]; then \
		cd $(SRC_DIR) && git pull; \
	else \
		git clone $(REPO) -b $(BRANCH) --depth 1 $(SRC_DIR); \
	fi

clone-opensbi:
	@if [ -d "$(OPENSBI_DIR)" ]; then \
		cd $(OPENSBI_DIR) && git pull; \
	else \
		git clone $(OPENSBI_REPO) -b $(OPENSBI_BRANCH) --depth 1 $(OPENSBI_DIR); \
	fi
	@cd $(OPENSBI_DIR) && make clean
	@cd $(OPENSBI_DIR) && make -j$(JOBS) CROSS_COMPILE=$(CROSS_COMPILE) PLATFORM_DEFCONFIG=k1_defconfig PLATFORM=generic

config: clone
	cd $(SRC_DIR) && make k1_defconfig

build: config
	cd $(SRC_DIR) && make -s -j$(JOBS) CROSS_COMPILE=$(CROSS_COMPILE) OPENSBI=$(OPENSBI_BLOB)

clean:
	rm -rf $(SRC_DIR) $(OPENSBI_DIR)
