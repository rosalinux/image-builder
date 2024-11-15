#!/usr/bin/env python
# -*- coding: utf-8 -*-

def build_uboot(config, vendor, device):
    if "UBOOT" not in config or "UBOOT_VERSION" not in config:
        print("U-Boot configuration not found. Skipping U-Boot build.")
        return

    uboot_dir = os.path.join(TMP_DIR, vendor, device, "u-boot")
    clone_repo(config["UBOOT"], config["UBOOT_VERSION"], uboot_dir, "U-Boot")

    os.chdir(uboot_dir)
    subprocess.run(["make", config["UBOOT_CONFIG"]], check=True)
    subprocess.run(["make", "-j" + NUM_CORES], check=True)

