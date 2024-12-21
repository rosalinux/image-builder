#!/usr/bin/env python

import os
import sys
import subprocess
import multiprocessing
from utils.bootstrap_setup import setup_bootstrap
from utils.common import load_config, clone_repo
from utils.make_disk import create_disk_image, setup_loop_device
from utils.make_disk import create_partitions, mount_partitions
from utils.generate_spec import generate_spec_file
from utils.kernel import clone_kernel, make_kernel_tar
from utils.uboot import build_uboot, flash_uboot
from utils.patch import apply_uboot_patches, apply_kernel_patches
from utils.rpmbuild import run_rpmbuild


BASE_DIR = os.getcwd()
TMP_DIR = os.path.join(BASE_DIR, "tmp")
NUM_CORES = str(multiprocessing.cpu_count())


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
    arch = config["ARCH"]

    print(f"Building for {vendor}/{device} with distro {distro}...")

    if not skip_kernel:
        kernel_dir = os.path.join(TMP_DIR, vendor, device, "kernel")
        clone_kernel(TMP_DIR, BASE_DIR, config, vendor, device, kernel_dir)
        generate_spec_file(TMP_DIR, config, vendor, device)
        kernel_rpm_dir = os.path.join(TMP_DIR, vendor, device, "kernel-build")
        make_kernel_tar(kernel_dir, kernel_rpm_dir)
        # Call rpmbuild to build the kernel RPM
        try:
            run_rpmbuild(kernel_rpm_dir, arch)
        except Exception as e:
            print(f"Failed to build RPM: {e}")
            sys.exit(1)
    else:
        print("Skipping kernel build.")

    if not skip_uboot:
        build_uboot(TMP_DIR, BASE_DIR, config, vendor, device)
    else:
        print("Skipping U-Boot build.")

    if not skip_rootfs:
        # dd here
        disk_image_path = create_disk_image(TMP_DIR, config, vendor, device)
        if disk_image_path:
            loop_device = setup_loop_device(disk_image_path)
            print(f"Loop device setup at {loop_device}")
        # fdisk, mkfs here
        create_partitions(loop_device, config)
        if not skip_uboot:
            flash_uboot(loop_device, TMP_DIR, config, vendor, device)
        mount_partitions(config, loop_device, TMP_DIR, vendor, device)
        # dnf install rootfs here
        setup_bootstrap("bootstrap", TMP_DIR, vendor, device, distro, arch)

    else:
        print("Skipping rootfs bootstrap")

    print(f"Build completed for {vendor}/{device} with distro {distro}")


if __name__ == "__main__":
    main()
