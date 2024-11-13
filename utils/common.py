#!/usr/bin/env python

def load_config(config_path):
    config = {}
    with open(config_path, "r") as f:
        for line in f:
            if "=" in line and not line.strip().startswith("#"):
                key, value = line.strip().split("=", 1)
                config[key] = value.strip('"')
    return config
