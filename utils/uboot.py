#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
from utils.common import clone_repo
from utils.common import download_blob
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
    blobs_url = config.get("BLOBS_URL", "")

    # Clone U-Boot repository
    uboot_dir = os.path.join(TMP_DIR, vendor, device, "u-boot")
    clone_repo(uboot_git, uboot_branch, uboot_dir, "u-boot")
    apply_uboot_patches(BASE_DIR, vendor, device, uboot_dir)

    # Download RK_DDR blob to uboot_dir
    rk_ddr = None
    if "RK_DDR" in config:
        rk_ddr = os.path.join(uboot_dir, os.path.basename(config.get("RK_DDR")))
        rk_ddr_url = os.path.join(blobs_url, os.path.basename(rk_ddr))
        if not os.path.isfile(rk_ddr):
            if not download_blob(rk_ddr_url, rk_ddr):
                print(f"Warning: RK_DDR blob {rk_ddr_url} could not be downloaded.")

    # Download BL31 blob to uboot_dir
    bl31 = None
    if "BL31" in config:
        bl31 = os.path.join(uboot_dir, os.path.basename(config.get("BL31")))
        bl31_url = os.path.join(blobs_url, os.path.basename(bl31))
        if not os.path.isfile(bl31):
            if not download_blob(bl31_url, bl31):
                print(f"Warning: BL31 blob {bl31_url} could not be downloaded.")

    # Build U-Boot
    os.chdir(uboot_dir)
    try:
        print(f"Building U-Boot for {vendor}/{device} {uboot_config}...")
        subprocess.run(["make", uboot_config], check=True)

        # Format U-Boot build command
        build_command = uboot_build_cmd.format(
            BL31=bl31 or "",
            ARCH=config.get("ARCH", "aarch64")
        )
        subprocess.run(build_command, shell=True, check=True)

        # Format mkimage command
        mkimage_command = mkimage_cmd.format(
            BOOT_SOC=config.get("BOOT_SOC", ""),
            RK_DDR=rk_ddr or ""
        )
        print(mkimage_command)
        subprocess.run(mkimage_command, shell=True, check=True)

        print("U-Boot build completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error during U-Boot build: {e}")
    os.chdir(BASE_DIR)
