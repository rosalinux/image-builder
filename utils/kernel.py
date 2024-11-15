#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import subprocess
from utils.common import clone_repo

def clone_kernel(TMP_DIR, config, vendor, device, kernel_dir):
    kernel_git = config.get("KERNEL").split("#")[0]
    kernel_branch = config.get("KERNEL").split("#")[1]
    clone_repo(kernel_git, kernel_branch, kernel_dir, "kernel")


def make_kernel_tar(kernel_dir, kernel_rpm_dir):
    os.chdir(kernel_dir)
    subprocess.run(["git", "archive",
                    "--format=tar", "--prefix=kernel/",
                    f"--output={kernel_rpm_dir}/kernel.tar", "HEAD"])
