#!/usr/bin/env python

import os
import sys
import subprocess
import multiprocessing
from utils.bootstrap_setup import setup_bootstrap
from utils.common import load_config
from utils.make_disk import create_disk_image, setup_loop_device
from utils.make_disk import create_partitions

BASE_DIR = os.getcwd()
TMP_DIR = os.path.join(BASE_DIR, "tmp")
NUM_CORES = str(multiprocessing.cpu_count())


def clone_repo(repo_url, branch, dest_dir, name):
    if os.path.exists(dest_dir):
        print(f"Warning: {name} directory '{dest_dir}' already exists. Skipping clone.")
    else:
        os.makedirs(dest_dir, exist_ok=True)
        subprocess.run(["git", "clone", "--depth", "1", repo_url, "-b", branch, dest_dir], check=True)


def build_kernel(config, vendor, device):
    kernel_dir = os.path.join(TMP_DIR, vendor, device, "kernel")
    clone_repo(config["KERNEL"].split("#")[0], config["KERNEL"].split("#")[1], kernel_dir, "Kernel")

    os.chdir(kernel_dir)
    subprocess.run(["make", config["KERNEL_CONFIG"]], check=True)
    subprocess.run(["make", "-j" + NUM_CORES], check=True)
    os.chdir(BASE_DIR)


def build_uboot(config, vendor, device):
    if "UBOOT" not in config or "UBOOT_VERSION" not in config:
        print("U-Boot configuration not found. Skipping U-Boot build.")
        return

    uboot_dir = os.path.join(TMP_DIR, vendor, device, "u-boot")
    clone_repo(config["UBOOT"], config["UBOOT_VERSION"], uboot_dir, "U-Boot")

    os.chdir(uboot_dir)
    subprocess.run(["make", config["UBOOT_CONFIG"]], check=True)
    subprocess.run(["make", "-j" + NUM_CORES], check=True)
    os.chdir(BASE_DIR)


def main():
    if len(sys.argv) < 3 or "--distro" not in sys.argv:
        print("example: python build.py --distro <distro_name> <vendor/device> [--skip-kernel] [--skip-uboot] [--skip-rootfs]")
        print("""Usage: optional features:
              --skip-kernel   [do not build kernel]
              --skip-uboot    [do not build u-boot]
              --skip-rootfs   [do not create distro rootfs]""")
        sys.exit(1)

    distro_idx = sys.argv.index("--distro") + 1
    distro = sys.argv[distro_idx]
    vendor_device = sys.argv[distro_idx + 1]
    vendor, device = vendor_device.split("/")
    config_path = os.path.join("device", vendor, device, "config")
    skip_kernel = "--skip-kernel" in sys.argv
    skip_uboot = "--skip-uboot" in sys.argv
    skip_rootfs = "--skip-rootfs" in sys.argv

    if not os.path.exists(config_path):
        print(f"Configuration file for {vendor}/{device} not found.")
        sys.exit(1)

    config = load_config(config_path)
    if config["ARCH"] != "aarch64":
        print("Unsupported architecture.")
        sys.exit(1)

    print(f"Building for {vendor}/{device} with distro {distro}...")

    if not skip_kernel:
        build_kernel(config, vendor, device)
    else:
        print("Skipping kernel build.")

    if not skip_uboot:
        build_uboot(config, vendor, device)
    else:
        print("Skipping U-Boot build.")

    if not skip_rootfs:
        setup_bootstrap("bootstrap", TMP_DIR, vendor, device, distro)
    else:
        print("Skipping rootfs bootstrap")

    disk_image_path = create_disk_image(TMP_DIR, config, vendor, device)
    if disk_image_path:
        loop_device = setup_loop_device(disk_image_path)
        print(f"Loop device setup at {loop_device}")
    create_partitions(loop_device, config)

    print(f"Build completed for {vendor}/{device} with distro {distro}")


if __name__ == "__main__":
    main()
