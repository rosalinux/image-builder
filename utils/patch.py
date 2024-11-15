#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess


def apply_patches(patch_dir, target_dir):
    """
    Applies patches from the specified patch directory to the target directory using `git apply`.
    """
    if not os.path.exists(patch_dir):
        print(f"No patches directory found at {patch_dir}. Skipping patch application.")
        return

    patches = sorted(os.listdir(patch_dir))

    if not patches:
        print(f"No patches found in {patch_dir}. Skipping patch application.")
        return

    print(f"Applying patches from {patch_dir} to {target_dir}...")

    for patch in patches:
        patch_path = os.path.join(patch_dir, patch)
        if os.path.isfile(patch_path):
            print(f"Applying patch: {patch}")
            try:
                subprocess.run(["git", "apply", patch_path], cwd=target_dir, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Failed to apply patch {patch}: {e}")
        else:
            print(f"Skipping non-file item: {patch_path}")


def apply_kernel_patches(base_dir, vendor, device, kernel_dir):
    """
    Apply kernel patches for the specified vendor and device.
    """
    patch_dir = os.path.join(base_dir, "device", vendor, device, "patches", "kernel")
    apply_patches(patch_dir, kernel_dir)


def apply_uboot_patches(base_dir, vendor, device, uboot_dir):
    """
    Apply U-Boot patches for the specified vendor and device.
    """
    patch_dir = os.path.join(base_dir, "device", vendor, device, "patches", "u-boot")
    apply_patches(patch_dir, uboot_dir)

