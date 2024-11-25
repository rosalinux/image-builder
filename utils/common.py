#!/usr/bin/env python
import os
import subprocess
from urllib.request import urlretrieve

def load_config(config_path):
    config = {}
    with open(config_path, "r") as f:
        for line in f:
            if "=" in line and not line.strip().startswith("#"):
                key, value = line.strip().split("=", 1)
                config[key] = value.strip('"')
    return config


def clone_repo(repo_url, branch, dest_dir, name):
    if os.path.exists(dest_dir):
        print(f"Warning: {name} directory '{dest_dir}' already exists. Skipping clone.")
    else:
        os.makedirs(dest_dir, exist_ok=True)
        subprocess.run(["git", "clone", "--depth", "1", repo_url, "-b", branch, dest_dir], check=True)


def download_blob(blob_url, destination):
    """Download a file from the given URL and save it to the destination."""
    try:
        print(f"Downloading {blob_url} to {destination}...")
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        urlretrieve(blob_url, destination)
        print(f"Downloaded: {destination}")
        return True
    except Exception as e:
        print(f"Warning: Unable to download {blob_url}. {e}")
        return False
