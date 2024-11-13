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


def cleanup_loop_devices():
    result = subprocess.run(["losetup", "-l", "-O", "NAME"], capture_output=True, text=True)
    active_loops = result.stdout.splitlines()[1:]

    for loop_device in active_loops:
        loop_device = loop_device.strip()
        if loop_device:
            print(f"Detaching {loop_device}")
            subprocess.run(["sudo", "losetup", "-d", loop_device], check=False)


def setup_loop_device(disk_image_path):
    cleanup_loop_devices()

    cmd = ["sudo", "losetup", "-fP", "--show", disk_image_path]
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    loop_device = result.stdout.strip()
    print(f"Disk image mounted to loop device {loop_device}")
    return loop_device


def create_partitions(loop_device, config):
    root_size = config.get("ROOT_SIZE", "1024MB").rstrip("MB")
    root_fstype = config.get("ROOT_FSTYPE", "ext4")
    boot_size = config.get("BOOT_SIZE")
    boot_fstype = config.get("BOOT_FSTYPE", "vfat") if boot_size else None

    print(f"Creating partitions on {loop_device}...")

    if boot_size:
        boot_size = boot_size.rstrip("MB")
        fdisk_commands = f"""\nn\np\n\n\n+{boot_size}M\nn\np\n\n\n\nw"""
        subprocess.run(["sudo", "fdisk", "--wipe", "always", loop_device], input=fdisk_commands, text=True, check=True)
        print(f" - Formatting /boot as {boot_fstype} ({boot_size} MB)")
        subprocess.run(["sudo", "mkfs.vfat", "-F", "32", f"{loop_device}p1"], check=True)

        print(f" - Formatting root (/) as {root_fstype} ({root_size} MB)")
        subprocess.run(["sudo", "mkfs.ext4", f"{loop_device}p2"], check=True)

    else:
        fdisk_commands = f"""o\nn\np\n\n\n+{root_size}M\nw\n"""
        subprocess.run(["sudo", "fdisk", "--wipe", "always", loop_device], input=fdisk_commands, text=True, check=True)

        print(f" - Formatting single root (/) partition as {root_fstype} ({root_size} MB)")
        subprocess.run(["sudo", "mkfs.ext4", f"{loop_device}p1"], check=True)

    print("Partitioning and formatting complete.")


def mount_partitions(config, loop_device, tmp_dir, vendor, device):
    rootfs_dir = os.path.join(tmp_dir, vendor, device, "rootfs")
    os.makedirs(rootfs_dir, exist_ok=True)
    boot_partition = f"{loop_device}p1"
    root_partition = f"{loop_device}p2" if "BOOT_SIZE" in config else f"{loop_device}p1"

    if "BOOT_SIZE" in config:
        boot_dir = os.path.join(rootfs_dir, "boot")
        os.makedirs(boot_dir, exist_ok=True)

        print(f"Mounting /boot partition at {boot_dir}")
        subprocess.run(["sudo", "mount", boot_partition, boot_dir], check=True)

    print(f"Mounting root (/) partition at {rootfs_dir}")
    subprocess.run(["sudo", "mount", root_partition, rootfs_dir], check=True)
    print("Mounting complete.")
