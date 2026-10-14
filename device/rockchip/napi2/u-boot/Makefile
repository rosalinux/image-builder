# U-Boot build for NAPI2 (Rockchip RK3568)
#
# FLAVOR=mainline (default): upstream u-boot v2025.07 + napi2 port
#   (dts/defconfig patches in patches-mainline/, board dts ported from the
#   lab240 kernel dts, PMIC RK809 support for SD power).
#   Generic variant (as shipped on the board) can be built with
#   DEFCONFIG=generic-rk3568_defconfig (needs PATCHES cleared).
# FLAVOR=vendor: radxa vendor tree (next-dev-v2024.10, 2017.09 base)
#   + lab240 napi2 defconfig/dts patches.
#
# Artifacts are copied into the device directory by the `install` target:
#  - idbloader.img  (DDR init blob + SPL), written at sector 64
#  - u-boot.itb     (U-Boot proper + BL31), written at sector 16384

FLAVOR ?= mainline
CROSS_COMPILE := aarch64-linux-gnu-
JOBS := $(shell nproc)

ifeq ($(FLAVOR),mainline)
SRC_DIR   := u-boot-mainline
UBOOT_REPO := https://github.com/u-boot/u-boot.git
UBOOT_REF  := v2025.07
DEFCONFIG  := napi2-rk3568_defconfig
PATCHES    := $(sort $(wildcard patches-mainline/*.patch))
else
SRC_DIR   := u-boot-radxa
UBOOT_REPO := https://github.com/radxa/u-boot.git
UBOOT_REF  := next-dev-v2024.10
DEFCONFIG  := napi2-rk3568_defconfig
PATCHES    := $(sort $(wildcard patches-local/*.patch))
endif

# ----- rkbin blobs (versions shipped by the vendor NAPI2 image) -----
BL31     := rk3568_bl31_v1.44.elf
RKDDR    := rk3568_ddr_1560MHz_v1.21.bin
BOOT_SOC := rk3568

BLOB_DIR  := rkbin
RKBIN_URL := https://github.com/armbian/rkbin/raw/refs/heads/master/rk35

PATCH_STAMP  := $(SRC_DIR)/.patches-applied
CONFIG_STAMP := $(SRC_DIR)/.config-done

OUT_DIR := ..

default: install

setup:
	sudo dnf install -y gcc-aarch64-linux-gnu binutils-aarch64-linux-gnu \
		uboot-tools bison flex openssl-devel gnutls-devel bc dtc \
		python3 python3-pyelftools swig python2

# ----- Sources -----

clone: $(SRC_DIR)/.cloned

$(SRC_DIR)/.cloned:
	git clone $(UBOOT_REPO) --branch $(UBOOT_REF) --depth 1 $(SRC_DIR)
	touch $@

blobs: $(BLOB_DIR)/$(BL31) $(BLOB_DIR)/$(RKDDR)

$(BLOB_DIR)/$(BL31):
	mkdir -p $(BLOB_DIR)
	wget -q $(RKBIN_URL)/$(BL31) -O $@

$(BLOB_DIR)/$(RKDDR):
	mkdir -p $(BLOB_DIR)
	wget -q $(RKBIN_URL)/$(RKDDR) -O $@

# ----- Patches -----

patches: $(PATCH_STAMP)

$(PATCH_STAMP): $(SRC_DIR)/.cloned $(PATCHES)
ifneq ($(PATCHES),)
	cd $(SRC_DIR) && for p in $(PATCHES); do \
		patch -Np1 -i ../$$p || exit 1; \
	done
endif
	touch $@

# ----- Configuration -----

config: $(CONFIG_STAMP)

$(CONFIG_STAMP): $(PATCH_STAMP)
	cd $(SRC_DIR) && make CROSS_COMPILE=$(CROSS_COMPILE) $(DEFCONFIG)
	touch $@

# ----- Build -----

build: config blobs
ifeq ($(FLAVOR),mainline)
	cd $(SRC_DIR) && make -j$(JOBS) CROSS_COMPILE=$(CROSS_COMPILE) KCFLAGS="-Wno-error" \
		BL31=$(CURDIR)/$(BLOB_DIR)/$(BL31) \
		ROCKCHIP_TPL=$(CURDIR)/$(BLOB_DIR)/$(RKDDR) BINMAN_ALLOW_MISSING=1
else
	cd $(SRC_DIR) && make -j$(JOBS) CROSS_COMPILE=$(CROSS_COMPILE) KCFLAGS="-Wno-error" \
		BL31=$(CURDIR)/$(BLOB_DIR)/$(BL31) \
		spl/u-boot-spl.bin u-boot.dtb u-boot.itb
endif
	cd $(SRC_DIR) && tools/mkimage -n $(BOOT_SOC) -T rksd \
		-d $(CURDIR)/$(BLOB_DIR)/$(RKDDR):spl/u-boot-spl.bin idbloader.img

# ----- Install artifacts for mkosi -----

install: build
	cp -fv $(SRC_DIR)/idbloader.img $(OUT_DIR)/
	cp -fv $(SRC_DIR)/u-boot.itb $(OUT_DIR)/

clean:
	rm -rf u-boot-mainline u-boot-radxa $(BLOB_DIR)

.PHONY: default setup clone blobs patches config build install clean
