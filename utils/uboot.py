#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
from utils.common import clone_repo
from utils.common import download_blob
from utils.patch import apply_uboot_patches

def build_uboot(TMP_DIR, BASE_DIR, config, vendor, device):
    uboot_git = config.get("UBOOT")
    uboot_branch = config.get("UBOOT_VERSION")
    uboot_config = config.get("UBOOT_CONFIG")
    uboot_build_cmd = config.get("UBOOT_BUILD")
    mkimage_cmd = config.get("MKIMAGE_CMD")
    blobs_url = config.get("BLOBS_URL", "")
    uboot_dir = os.path.join(TMP_DIR, vendor, device, "u-boot")

    if "UBOOT" not in config or "UBOOT_VERSION" not in config:
        print("U-Boot configuration not found. Skipping U-Boot build.")
        return

    # Clone U-Boot repository
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

def flash_uboot(loop_device, TMP_DIR, config, vendor, device):
    """
    Flash U-Boot components to the disk image.
    Parameters:
        loop_device (str): The loop device path (e.g., /dev/loop0).
        uboot_dir (str): Directory where U-Boot artifacts are located.
        config (dict): Configuration dictionary.
    """
    uboot_dir = os.path.join(TMP_DIR, vendor, device, "u-boot")
    idbloader_path = os.path.join(uboot_dir, config.get("BOOT_IDB", "idbloader.img"))
    uboot_itb_path = os.path.join(uboot_dir, config.get("BOOT_ITB", "u-boot.itb"))

    if not os.path.isfile(idbloader_path) or not os.path.isfile(uboot_itb_path):
        print(f"Error: Required U-Boot files not found: {idbloader_path}, {uboot_itb_path}")
        return False

    try:
        print(f"Flashing {idbloader_path} to {loop_device}...")
        subprocess.run([
            "dd", f"if={idbloader_path}", f"of={loop_device}", "seek=64", 
            "conv=notrunc", "status=none"
        ], check=True)

        print(f"Flashing {uboot_itb_path} to {loop_device}...")
        subprocess.run([
            "dd", f"if={uboot_itb_path}", f"of={loop_device}", "seek=16384",
            "conv=notrunc", "status=none"
        ], check=True)

        print("U-Boot flashing completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error flashing U-Boot files: {e}")
        return False

    return True
