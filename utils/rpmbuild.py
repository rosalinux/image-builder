#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import subprocess


def run_rpmbuild(kernel_build_dir, target_arch):
    """Run rpmbuild for the given kernel build directory and target architecture."""
    # Ensure the kernel-build directory exists
    if not os.path.isdir(kernel_build_dir):
        print(f"Error: Kernel build directory '{kernel_build_dir}' does not exist.")
        sys.exit(1)

    # Change to the kernel-build directory
    os.chdir(kernel_build_dir)

    # Check if a spec file exists
    spec_files = [f for f in os.listdir(kernel_build_dir) if f.endswith(".spec")]
    if not spec_files:
        print(f"Error: No spec files found in '{kernel_build_dir}'.")
        sys.exit(1)
    elif len(spec_files) > 1:
        print(f"Warning: Multiple spec files found in '{kernel_build_dir}'. Using '{spec_files[0]}'.")

    # Use the first spec file found
    spec_file = spec_files[0]

    # Define paths for RPM build directories
    rpmdir = os.path.join(kernel_build_dir, "RPMS")
    builddir = os.path.join(kernel_build_dir, "BUILD")
    os.makedirs(rpmdir, exist_ok=True)
    os.makedirs(builddir, exist_ok=True)

    # Construct the rpmbuild command
    rpmbuild_command = [
        "rpmbuild", "-ba",
        f"--target={target_arch}",
        f"--define", f"_sourcedir {kernel_build_dir}",
        f"--define", f"_rpmdir {rpmdir}",
        f"--define", f"_builddir {builddir}",
        spec_file
    ]

    # Run the rpmbuild command
    try:
        print(f"Running rpmbuild for spec file: {spec_file} with target architecture: {target_arch}")
        #subprocess.run(rpmbuild_command, check=True)
        subprocess.run(
            rpmbuild_command,
            stdin=subprocess.DEVNULL,  # Отключение ввода
            stdout=sys.stdout,         # Вывод в стандартный поток
            stderr=sys.stderr,         # Вывод ошибок
            check=True
        )
        print(f"RPM build completed successfully. RPMs are located in: {rpmdir}")
    except subprocess.CalledProcessError as e:
        print(f"Error: rpmbuild failed with error code {e.returncode}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: rpmbuild.py <kernel-build-dir> <target-arch>")
        sys.exit(1)

    kernel_build_dir = sys.argv[1]
    target_arch = sys.argv[2]
    run_rpmbuild(kernel_build_dir, target_arch)
