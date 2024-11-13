#!/usr/bin/env python

import os
import subprocess


def create_disk_image(tmp_dir, config, vendor, device):

    boot_size = config.get("BOOT_SIZE").rstrip("MB")
    root_size = config.get("ROOT_SIZE").rstrip("MB")

    if not root_size:
        print("Error: ROOT_SIZE is not defined in the configuration.")
        return

    if not boot_size:
        boot_size = "0"

    disk_image_path = os.path.join(tmp_dir, vendor, device, "disk.img")
    cmd = [
        "dd",
        "if=/dev/zero",
        f"of={disk_image_path}",
        "bs=1M",
        f"count={int(boot_size) + int(root_size)}"
    ]

    print(f"Creating disk image: {disk_image_path} size {root_size} MB")
    subprocess.run(cmd, check=True)
    print(f"Disk image created at {disk_image_path}")
    return disk_image_path


def setup_loop_device(disk_image_path):
    print("Cleanup /dev/loopX leftovers")
    leftovers = ["sudo", "losetup", "-d", "/dev/loop*"]
    subprocess.run(leftovers, check=False)

    cmd = ["sudo", "losetup", "-fP", "--show", disk_image_path]
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    loop_device = result.stdout.strip()
    print(f"Disk image mounted to loop device {loop_device}")
    return loop_device
