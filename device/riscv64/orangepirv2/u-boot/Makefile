CROSS_COMPILE := riscv64-linux-gnu-
JOBS := $(shell nproc)
BRANCH := v2022.10-ky
REPO := https://github.com/orangepi-xunlong/u-boot-orangepi.git
SRC_DIR := u-boot-orangepi

default: clone build

setup:
	sudo dnf install -y gcc-riscv64-linux-gnu binutils-riscv64-linux-gnu

clone:
	@if [ -d "$(SRC_DIR)" ]; then \
		cd $(SRC_DIR) && git pull; \
	else \
		git clone $(REPO) -b $(BRANCH) --depth 1 $(SRC_DIR); \
	fi

config:
	cd $(SRC_DIR) && make x1_defconfig

build: config
	cd $(SRC_DIR) && make -s -j$(JOBS) CROSS_COMPILE=$(CROSS_COMPILE)

clean:
	rm -rf $(SRC_DIR)
