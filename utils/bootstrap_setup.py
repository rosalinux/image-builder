import os
import sys
import subprocess


def load_config(config_path):
    config = {}
    with open(config_path, "r") as f:
        for line in f:
            if "=" in line and not line.strip().startswith("#"):
                key, value = line.strip().split("=", 1)
                config[key] = value.strip('"')
    return config


def load_bootstrap_config(bootstrap_path):
    """Load the bootstrap configuration from the specified file."""
    config = {}
    with open(bootstrap_path, "r") as f:
        for line in f:
            if "=" in line and not line.strip().startswith("#"):
                key, value = line.strip().split("=", 1)
                config[key] = value.strip('"')
    return config


def generate_dnf_conf(dnf_conf_path, abf_downloads, release):
    """Generate dnf.conf based on the bootstrap configuration."""
    dnf_conf_content = f"""
[main]
keepcache=1
debuglevel=2
reposdir=/dev/null
retries=20
obsoletes=1
gpgcheck=0
assumeyes=1
syslog_ident=mock
syslog_device=
install_weak_deps=0
metadata_expire=60s
best=1

[{release}_main_release]
name={release}_main_release
baseurl={abf_downloads}/{release}/repository/aarch64/main/release
gpgcheck=0
enabled=1

[{release}_main_updates]
name={release}_main_updates
baseurl={abf_downloads}/{release}/repository/aarch64/main/updates
gpgcheck=0
enabled=1
"""

    os.makedirs(os.path.dirname(dnf_conf_path), exist_ok=True)
    with open(dnf_conf_path, "w") as f:
        f.write(dnf_conf_content)


def run_dnf_install(config, dnf_conf_path, rootfs_dir):
    """Run dnf command to install packages based on the bootstrap configuration."""
    pkgs = config["PKGS"]
    weak_deps = config["WEAK_DEPS"].lower()

    dnf_command = [
        "sudo",
        "dnf",
        "--setopt=install_weak_deps=" + str(weak_deps),
        "--config", dnf_conf_path,
        "--installroot", rootfs_dir,
        "install"
    ] + pkgs.split()

    subprocess.run(dnf_command, check=True)


def setup_bootstrap(bootstrap_dir, tmp_dir, vendor, device, distro):
    # load distro config
    # bootstrap/DISTRO_NAME
    distro_config_path = os.path.join(bootstrap_dir, distro)
    if not os.path.exists(distro_config_path):
        print(f"Bootstrap configuration for distro '{distro}' not found.")
        sys.exit(1)

    config = load_config(distro_config_path)

    dnf_conf_path = os.path.join(tmp_dir, vendor, device, "dnf.conf")
    rootfs_dir = os.path.join(tmp_dir, vendor, device, "rootfs")

    generate_dnf_conf(dnf_conf_path, config["ABF_DOWNLOADS"], config["RELEASE"])
    run_dnf_install(config, dnf_conf_path, rootfs_dir)

    #setup_user(rootfs_dir, config["DEFAULT_USER"], config["DEFAULT_USER_PASSWORD"], config["PASSWD_ROOT"])
