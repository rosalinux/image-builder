# Firmware build for Milk-V Jupiter2 (SpacemiT K3, RISC-V64)
#
# Components (built from source):
#  1. U-Boot  (spacemit-com/uboot-2022.10, branch k3-br-v1.0.y, k3_defconfig)
#     -> FSBL.bin, bootinfo*.bin, u-boot.itb, u-boot-env-default.bin
#  2. EDK2    (spacemit-com/edk2-spacemit, vendored edk2 + edk2-platforms)
#     -> edk2.itb  (UEFI payload, Platform/Spacemit/K3/MUSE-Pico)
#
# Build recipe for EDK2 mirrors edk2-spacemit/debian/rules.
#
# Artifacts are copied into ../firmware/ by the `install` target.

CROSS_COMPILE := riscv64-linux-gnu-
JOBS := $(shell nproc)

# ----- U-Boot -----
UBOOT_REPO := https://github.com/spacemit-com/uboot-2022.10.git
UBOOT_REF  := k3-br-v1.0.y
UBOOT_DIR  := u-boot-spacemit
UBOOT_DEFCONFIG := k3_defconfig

# ----- OpenSBI (fw_dynamic.itb loaded at the opensbi partition) -----
OPENSBI_REPO := https://github.com/spacemit-com/opensbi.git
OPENSBI_REF  := k3-br-v1.0.y
OPENSBI_DIR  := opensbi
OPENSBI_ITB  := $(OPENSBI_DIR)/build/platform/generic/firmware/fw_dynamic.itb

OPENSBI_STAMP := $(OPENSBI_DIR)/.build-done

# ----- EDK2 (UEFI) -----
EDK2_REPO := https://github.com/spacemit-com/edk2-spacemit.git
EDK2_REF  := main
EDK2_DIR  := edk2-spacemit
EDK2_DSC  := Platform/Spacemit/K3/MUSE-Pico/MUSE-Pico.dsc
EDK2_ITB  := fitimage/MUSE-Pico/MUSE-Pico.itb

UBOOT_STAMP := $(UBOOT_DIR)/.build-done
EDK2_STAMP  := $(EDK2_DIR)/.build-done

OUT_DIR := ../firmware

default: install

setup:
	sudo dnf install -y gcc-riscv64-linux-gnu binutils-riscv64-linux-gnu \
		uboot-tools bison flex openssl-devel gnutls-devel bc dtc swig \
		python3 python3-pyelftools python3-setuptools acpica libuuid-devel git

# ----- U-Boot -----

clone: $(UBOOT_DIR)/.cloned

$(UBOOT_DIR)/.cloned:
	git clone $(UBOOT_REPO) --branch $(UBOOT_REF) --depth 1 $(UBOOT_DIR)
	touch $@

uboot: $(UBOOT_STAMP)

$(UBOOT_STAMP): $(UBOOT_DIR)/.cloned
	cd $(UBOOT_DIR) && make CROSS_COMPILE=$(CROSS_COMPILE) $(UBOOT_DEFCONFIG)
# SPL_SIZE_LIMIT=0x72F00 is tight: the generic riscv64 toolchain emits a
# slightly larger SPL than the SpacemiT vendor one used for the official
# builds, so shave the timestamp printer (as the K1 Alpine recipe does).
	cd $(UBOOT_DIR) && scripts/config --file .config --disable PRINT_TIMESTAMP
# SPL_SIZE_LIMIT=0x72F00 assumes the SpacemiT vendor toolchain; gcc 14 emits
# ~1.5K more code. The FSBL slot is 512K (see partition_universal.json) and
# our FSBL is ~466K, so allow up to 0x78000.
	cd $(UBOOT_DIR) && scripts/config --file .config --set-val SPL_SIZE_LIMIT 0x78000
	cd $(UBOOT_DIR) && make -j$(JOBS) CROSS_COMPILE=$(CROSS_COMPILE) \
		KCFLAGS="-Wno-error"
	touch $@

# ----- OpenSBI -----

opensbi: $(OPENSBI_STAMP)

$(OPENSBI_STAMP): $(OPENSBI_DIR)/.cloned
	cd $(OPENSBI_DIR) && make -j$(JOBS) CROSS_COMPILE=$(CROSS_COMPILE) \
		PLATFORM=generic PLATFORM_DEFCONFIG=k3_defconfig
	touch $@

# ----- EDK2 -----

clone-edk2: $(EDK2_DIR)/.cloned

$(EDK2_DIR)/.cloned:
	git clone $(EDK2_REPO) --branch $(EDK2_REF) --depth 1 $(EDK2_DIR)
	touch $@

clone-opensbi: $(OPENSBI_DIR)/.cloned

$(OPENSBI_DIR)/.cloned:
	git clone $(OPENSBI_REPO) --branch $(OPENSBI_REF) --depth 1 $(OPENSBI_DIR)
	touch $@

edk2: $(EDK2_STAMP)

$(EDK2_STAMP): $(EDK2_DIR)/.cloned
# rosa multilib quirk: the 64-bit libuuid.so dev symlink lives in the 32-bit
# /usr/lib dir; provide a proper one and put it first on the linker path.
	mkdir -p $(EDK2_DIR)/.hostlibs
	ln -sf /usr/lib64/libuuid.so.1 $(EDK2_DIR)/.hostlibs/libuuid.so
	cd $(EDK2_DIR) && bash -c "source edk2/edksetup.sh && \
		LIBRARY_PATH=$$PWD/.hostlibs make -C edk2/BaseTools -j$(JOBS)"
	cd $(EDK2_DIR) && bash -c "export WORKSPACE=$$PWD \
		PACKAGES_PATH=$$PWD/edk2:$$PWD/edk2-platforms \
		GCC5_RISCV64_PREFIX=$(CROSS_COMPILE) ; \
		source edk2/edksetup.sh && \
		build -a RISCV64 -p $(EDK2_DSC) -t GCC5 -b RELEASE -n $(JOBS)"
	cp -fv $(EDK2_DIR)/$(EDK2_ITB) $(EDK2_DIR)/edk2.itb
	touch $@

# ----- Install artifacts -----

install: uboot opensbi edk2
	mkdir -p $(OUT_DIR)
	cp -fv $(UBOOT_DIR)/FSBL.bin $(OUT_DIR)/ 2>/dev/null || true
	cp -fv $(UBOOT_DIR)/bootinfo*.bin $(OUT_DIR)/ 2>/dev/null || true
	cp -fv $(UBOOT_DIR)/u-boot.itb $(OUT_DIR)/ 2>/dev/null || true
	cp -fv $(UBOOT_DIR)/u-boot-env-default.bin $(OUT_DIR)/ 2>/dev/null || true
	cp -fv $(OPENSBI_ITB) $(OUT_DIR)/
	cp -fv $(EDK2_DIR)/edk2.itb $(OUT_DIR)/
	ls -la $(OUT_DIR)/

clean:
	rm -rf $(UBOOT_DIR) $(EDK2_DIR) $(OUT_DIR)

.PHONY: default setup clone uboot clone-edk2 clone-opensbi edk2 opensbi install clean
