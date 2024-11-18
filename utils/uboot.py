#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
from utils.common import clone_repo
from utils.patch import apply_uboot_patches


def build_uboot(TMP_DIR, BASE_DIR, config, vendor, device):
    if "UBOOT" not in config or "UBOOT_VERSION" not in config:
        print("U-Boot configuration not found. Skipping U-Boot build.")
        return

    uboot_git = config.get("UBOOT")
    uboot_branch = config.get("UBOOT_VERSION")
    uboot_config = config.get("UBOOT_CONFIG")
    uboot_build_cmd = config.get("UBOOT_BUILD")
    mkimage_cmd = config.get("MKIMAGE_CMD")

    blobs_dir = os.path.join(BASE_DIR, "device", vendor, device, "blobs")
    rk_ddr = os.path.join(blobs_dir, config.get("RK_DDR", ""))
    bl31 = os.path.join(blobs_dir, config.get("BL31", ""))

    if not os.path.isfile(rk_ddr) or not os.path.isfile(bl31):
        print(f"Missing required files in blobs directory: {rk_ddr}, {bl31}")
        return

    uboot_dir = os.path.join(TMP_DIR, vendor, device, "u-boot")
    clone_repo(uboot_git, uboot_branch, uboot_dir, "u-boot")
    apply_uboot_patches(BASE_DIR, vendor, device, uboot_dir)

    os.chdir(uboot_dir)
    try:
        print(f"Building U-Boot for {vendor}/{device} {uboot_config}...")
        subprocess.run(["make", uboot_config], check=True)
        build_command = uboot_build_cmd.format(BL31=bl31, ARCH=config.get("ARCH", "aarch64"))
        subprocess.run(build_command, shell=True, check=True)
        mkimage_command = mkimage_cmd.format(BOOT_SOC=config.get("BOOT_SOC", ""), RK_DDR=rk_ddr)
        subprocess.run(mkimage_command, shell=True, check=True)
        print("U-Boot build completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error during U-Boot build: {e}")

