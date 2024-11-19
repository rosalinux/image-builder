#!/usr/bin/env python

import os
import subprocess


def create_disk_image(tmp_dir, config, vendor, device):

    boot_size = config.get("BOOT_SIZE", "").rstrip("MB")
    root_size = config.get("ROOT_SIZE", "0").rstrip("MB")

    if not root_size:
        print("Error: ROOT_SIZE is not defined in the configuration.")
        return

    if not boot_size:
        boot_size = "0"

    disk_image_path = os.path.join(tmp_dir, vendor, device, "disk.img")
    os.makedirs(os.path.dirname(disk_image_path), exist_ok=True)
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


def cleanup_loop_devices():
    result = subprocess.run(["losetup", "-l", "-O", "NAME"], capture_output=True, text=True)
    active_loops = result.stdout.splitlines()[1:]

    for loop_device in active_loops:
        loop_device = loop_device.strip()
        if loop_device:
            print(f"Detaching {loop_device}")
            subprocess.run(["losetup", "-d", loop_device], check=False)


def setup_loop_device(disk_image_path):
    cleanup_loop_devices()

    cmd = ["losetup", "-fP", "--show", disk_image_path]
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    loop_device = result.stdout.strip()
    print(f"Disk image mounted to loop device {loop_device}")
    return loop_device

def create_partitions(loop_device, config):
    root_size = config.get("ROOT_SIZE", "1024MB").rstrip("MB")
    root_fstype = config.get("ROOT_FSTYPE", "ext4")
    boot_size = config.get("BOOT_SIZE", "0").rstrip("MB")  # Default to 0 if not specified
    boot_fstype = config.get("BOOT_FSTYPE", "ext4") # Default to ext4 if not specified

    print(f"Creating partitions on {loop_device} using sgdisk...")

    try:
        # Clear existing partitions
        subprocess.run(["sgdisk", "--zap-all", loop_device], check=True)

        if int(boot_size) > 0:
            # Create boot partition
            # 16M here s empty space for u-boot
            subprocess.run(["sgdisk",
                            "--new=1:16M:+{}M".format(boot_size),
                            "--typecode=1:8300", loop_device], check=True)

            # Create root partition
            subprocess.run(["sgdisk",
                            "--new=2:0:0",
                            "--typecode=2:8300", loop_device], check=True)

            # Format partitions
            if boot_fstype == "vfat":
                subprocess.run(["mkfs.vfat", "-F", "32", f"{loop_device}p1"], check=True)
            else:
                subprocess.run(["mkfs.ext4", f"{loop_device}p1"], check=True)
            subprocess.run(["mkfs.ext4", f"{loop_device}p2"], check=True)

            print(f" - Boot partition ({boot_size}MB) created and formatted as {boot_fstype}")
            print(f" - Root partition created and formatted as {root_fstype}")

        else:
            # Create single root partition
            subprocess.run(["sgdisk", "--new=1:0:0", "--typecode=1:8300", loop_device], check=True)
            subprocess.run(["mkfs.ext4", f"{loop_device}p1"], check=True)
            print(f" - Single root partition created and formatted as {root_fstype}")

    except subprocess.CalledProcessError as e:
        print(f"Error creating partitions with sgdisk: {e}")
        return False

    print("Partitioning and formatting complete.")
    return True

def mount_partitions(config, loop_device, tmp_dir, vendor, device):
    rootfs_dir = os.path.join(tmp_dir, vendor, device, "rootfs")
    os.makedirs(rootfs_dir, exist_ok=True)
    boot_partition = f"{loop_device}p1"
    root_partition = f"{loop_device}p2" if "BOOT_SIZE" in config else f"{loop_device}p1"

    print(f"Mounting root (/) partition at {rootfs_dir}")
    subprocess.run(["mount", root_partition, rootfs_dir], check=True)

    if "BOOT_SIZE" in config:
        boot_dir = os.path.join(rootfs_dir, "boot")
        os.makedirs(boot_dir, exist_ok=True)
        print(f"Mounting /boot partition at {boot_dir}")
        subprocess.run(["mount", boot_partition, boot_dir], check=True)

    print("Mounting complete.")
