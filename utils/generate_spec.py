#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from common import load_config

def get_kernel_version(kernel_url, branch):
    """Extract kernel version from kernel URL and branch"""
    return branch

def generate_spec_file(vendor, device):
    """Generate RPM spec file from template and config"""
    # Load device config
    config_path = os.path.join("device", vendor, device, "config")
    if not os.path.exists(config_path):
        print(f"Error: Config file not found at {config_path}")
        sys.exit(1)

    config = load_config(config_path)

    # Load template
    template_path = os.path.join("utils", "kernel.template")
    if not os.path.exists(template_path):
        print(f"Error: Template file not found at {template_path}")
        sys.exit(1)

    with open(template_path, 'r') as f:
        template = f.read()

    # Extract kernel version from kernel URL and branch
    kernel_url, kernel_branch = config["KERNEL"].split("#")
    kernel_version = get_kernel_version(kernel_url, kernel_branch)

    # Determine KERNEL_ARCH and CROSS_COMPILE based on ARCH
    arch = config.get("ARCH", "unknown")
    kernel_config = config.get("KERNEL_CONFIG", "unknown")
    if arch == "aarch64":
        kernel_arch = "arm64"
        cross_compile = "aarch64-linux-gnu"
    else:
        kernel_arch = arch
        cross_compile = f"{arch}-linux-gnu"  # Default cross compile format

    # Prepare replacements
    device_name = f"{vendor}-{device}"
    replacements = {
        "{BOARD_NAME}": device_name,
        "{KERNEL_VERSION}": kernel_version,
        "{DEVICE_NAME}": device_name,
        "{KERNEL_ARCH}": kernel_arch,
        "{ARCH}": arch,  # Add ARCH replacement
        "{KERNEL_CONFIG}": kernel_config,  # Add ARCH replacement
        "{CROSS_COMPILE}": cross_compile  # Add CROSS_COMPILE replacement
    }

    # Apply replacements
    spec_content = template
    for key, value in replacements.items():
        spec_content = spec_content.replace(key, value)

    # Define output directory and path
    output_dir = os.path.join("tmp", vendor, device, "kernel-build")
    os.makedirs(output_dir, exist_ok=True)

    # Write spec file
    spec_file_path = os.path.join(output_dir, f"kernel-{device_name}.spec")
    with open(spec_file_path, 'w') as f:
        f.write(spec_content)

    print(f"Generated spec file: {spec_file_path}")
    return spec_file_path

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: generate_spec.py <vendor> <device>")
        sys.exit(1)

    vendor = sys.argv[1]
    device = sys.argv[2]

    generate_spec_file(vendor, device)

