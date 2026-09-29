# U-Boot build for Orange Pi RV2 (SpacemiT K1) following the
# aports/testing/u-boot-spacemit/APKBUILD recipe (Alpine Linux).
#
# Differences from the old scheme:
#  - source: official spacemit-com/uboot-2022.10 fork (release tag)
#    instead of pyavitz/spacemit-u-boot
#  - OpenSBI: mainline (riscv-software-src/opensbi, tag v1.9 as in
#    aports/main/opensbi), embedded into u-boot.itb by the
#    k1-bl-v2.2.y-opensbi-embeded.patch — a separate fw_dynamic.itb
#    is no longer needed
#  - artifacts are copied into the device directory by the `install` target

CROSS_COMPILE := riscv64-linux-gnu-
JOBS := $(shell nproc)

# ----- U-Boot (as in APKBUILD: source=.../k1-bl-v2.2.10-release.tar.gz) -----
UBOOT_REPO := https://github.com/spacemit-com/uboot-2022.10.git
UBOOT_TAG  := k1-bl-v2.2.10-release
SRC_DIR    := u-boot-spacemit

# ----- Mainline OpenSBI (replaces the opensbi package from makedepends;
# tag as in aports/main/opensbi/APKBUILD) -----
OPENSBI_REPO := https://github.com/riscv-software-src/opensbi.git
OPENSBI_TAG  := v1.9
OPENSBI_DIR  := opensbi
OPENSBI_BLOB := $(CURDIR)/$(OPENSBI_DIR)/build/platform/generic/firmware/fw_dynamic.bin

# ----- Patches -----
APORTS_UBOOT   := $(CURDIR)/../aports/testing/u-boot-spacemit
LOCAL_PATCHES  := $(sort $(wildcard patches-local/*.patch))
# Order follows the source= array of the APKBUILD
APORTS_PATCHES := \
	002-SpacemiT-K1X-Fixups.patch \
	003-SpacemiT-K1X-Defconfig-Fixups.patch \
	005-Orange-Pi-RV2-u-boot-support-for-XM25QU128C-flash.patch \
	006-orangepi-rv2-r2s-fit.patch \
	use-mainline-opensbi.patch \
	0001-k1-x_MUSE-Book.dts-add-P1-regulator-to-MUSE-Book-boa.patch \
	k1-bl-v2.2.y-opensbi-embeded.patch

PATCH_STAMP := $(SRC_DIR)/.patches-applied
CONFIG_STAMP := $(SRC_DIR)/.config-done

OUT_DIR := ..

default: install

setup:
	sudo dnf install -y gcc-riscv64-linux-gnu binutils-riscv64-linux-gnu \
		uboot-tools bison flex openssl-devel bc dtc python3 python3-pyelftools swig

# ----- Sources -----

clone: $(SRC_DIR)/.cloned

$(SRC_DIR)/.cloned:
	git clone $(UBOOT_REPO) --branch $(UBOOT_TAG) --depth 1 $(SRC_DIR)
	touch $@

clone-opensbi: $(OPENSBI_DIR)/.cloned

$(OPENSBI_DIR)/.cloned:
	git clone $(OPENSBI_REPO) --branch $(OPENSBI_TAG) --depth 1 $(OPENSBI_DIR)
	touch $@

# OpenSBI: mainline, generic platform -> fw_dynamic.bin (embedded into u-boot.itb)
opensbi: $(OPENSBI_BLOB)

$(OPENSBI_BLOB): $(OPENSBI_DIR)/.cloned
	$(MAKE) -C $(OPENSBI_DIR) -j$(JOBS) CROSS_COMPILE=$(CROSS_COMPILE) PLATFORM=generic

# ----- Patches (order as in APKBUILD source=, then local ones) -----

patches: $(PATCH_STAMP)

$(PATCH_STAMP): $(SRC_DIR)/.cloned $(APORTS_PATCHES:%=$(APORTS_UBOOT)/%) $(LOCAL_PATCHES)
	cd $(SRC_DIR) && for p in $(APORTS_PATCHES); do \
		patch -Np1 -i $(APORTS_UBOOT)/$$p || exit 1; \
	done
	cp -f $(APORTS_UBOOT)/k1-x.env $(SRC_DIR)/board/spacemit/k1-x/k1-x.env
	cd $(SRC_DIR) && for p in $(LOCAL_PATCHES); do \
		patch -Np1 -i $(CURDIR)/$$p || exit 1; \
	done
	touch $@

# ----- Configuration (mirrors prepare() from the APKBUILD) -----

config: $(CONFIG_STAMP)

$(CONFIG_STAMP): $(PATCH_STAMP)
	cd $(SRC_DIR) && make k1_defconfig
	cd $(SRC_DIR) && scripts/config --file .config --disable PRINT_TIMESTAMP
	cd $(SRC_DIR) && scripts/config --file .config --set-val BOOTDELAY 2
	cd $(SRC_DIR) && scripts/config --file .config --disable AUTOBOOT_KEYED
	cd $(SRC_DIR) && scripts/config --file .config --disable AUTOBOOT_USE_MENUKEY
	cd $(SRC_DIR) && scripts/config --file .config --disable LOCALVERSION_AUTO
	cd $(SRC_DIR) && scripts/config --file .config --disable AUTOBOOT_DELAY_STR
	cd $(SRC_DIR) && scripts/config --file .config --disable AUTOBOOT_STOP_STR
	cd $(SRC_DIR) && scripts/config --file .config --disable ENV_IS_IN_NFS
	cd $(SRC_DIR) && scripts/config --file .config --enable VIDEO_MIPI_DSI
	cd $(SRC_DIR) && scripts/config --file .config --enable ENV_IS_IN_SPI_FLASH
	cd $(SRC_DIR) && scripts/config --file .config --enable USE_PREBOOT
	cd $(SRC_DIR) && scripts/config --file .config --set-str PREBOOT "usb start"
	cd $(SRC_DIR) && scripts/config --file .config --set-str LOCALVERSION " 2.2.10"
	touch $@

# ----- Build (mirrors build() from the APKBUILD: OPENSBI is embedded into u-boot.itb) -----

build: config opensbi
	cd $(SRC_DIR) && make -j$(JOBS) CROSS_COMPILE=$(CROSS_COMPILE) OPENSBI=$(OPENSBI_BLOB)

# ----- Install artifacts for mkosi -----

install: build
	cp -fv $(SRC_DIR)/FSBL.bin $(OUT_DIR)/
	cp -fv $(SRC_DIR)/bootinfo_sd.bin $(OUT_DIR)/
	cp -fv $(SRC_DIR)/u-boot.itb $(OUT_DIR)/
	cp -fv $(SRC_DIR)/u-boot-env-default.bin $(OUT_DIR)/
	rm -f $(OUT_DIR)/fw_dynamic.itb

clean:
	rm -rf $(SRC_DIR) $(OPENSBI_DIR)

.PHONY: default setup clone clone-opensbi opensbi patches config build install clean
