#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
from utils.common import clone_repo
from utils.patch import apply_uboot_patches


def build_uboot(TMP_DIR, BASE_DIR, config, vendor, device):
    uboot_git = config.get("UBOOT")
    uboot_branch = config.get("UBOOT_VERSION")

    if "UBOOT" not in config or "UBOOT_VERSION" not in config:
        print("U-Boot configuration not found. Skipping U-Boot build.")
        return

    uboot_dir = os.path.join(TMP_DIR, vendor, device, "u-boot")
    clone_repo(uboot_git, uboot_branch, uboot_dir, "u-boot")
    apply_uboot_patches(BASE_DIR, vendor, device, uboot_dir)


    #os.chdir(uboot_dir)
    #subprocess.run(["make", config["UBOOT_CONFIG"]], check=True)
    #subprocess.run(["make", "-j" + NUM_CORES], check=True)

