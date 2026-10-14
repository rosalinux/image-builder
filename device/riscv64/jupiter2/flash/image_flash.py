#!/usr/bin/env python3
"""Extract partitions from a raw image and flash a SpacemiT K3 board.

Own implementation of the K3-Ubuntu-Images flash flow (fastboot protocol
is trivial: getvar / stage / continue / flash). Partition offsets come
from partition_universal.json, the same file the on-device u-boot
fastboot accepts for `fastboot flash gpt`.

Usage:
    image_flash.py --img ../image.raw --partition partition_universal.json
    image_flash.py --fastboot            # assumes ./temp populated
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

TEMP_DIR = Path("temp")
COPY_CHUNK = 4 * 1024 * 1024


def parse_size(s: str) -> int:
    s = str(s).strip()
    if s in ("-", ""):
        return -1
    units = {"K": 1024, "M": 1024**2, "G": 1024**3}
    if s[-1].upper() in units:
        return int(s[:-1]) * units[s[-1].upper()]
    return int(s, 0)


def load_json(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def _copy(src_f, dst_path: Path, size: int, label: str):
    total = 0
    with open(dst_path, "wb") as dst:
        while size < 0 or total < size:
            want = COPY_CHUNK if size < 0 else min(COPY_CHUNK, size - total)
            chunk = src_f.read(want)
            if not chunk:
                break
            dst.write(chunk)
            total += len(chunk)
    print(f"  [extract] {label}: {total:,} bytes -> {dst_path}")


def extract(img_path: str, partition_json: str):
    cfg = load_json(partition_json)
    parts = [p for p in cfg["partitions"] if p.get("image")]
    parts.sort(key=lambda p: parse_size(p["offset"]))
    TEMP_DIR.mkdir(exist_ok=True)
    with open(img_path, "rb") as src:
        pos = 0
        for p in parts:
            off = parse_size(p["offset"])
            size = parse_size(p["size"])
            src.seek(off)
            _copy(src, TEMP_DIR / p["image"], size, p["name"])


def _run(cmd: list, retry: int = 1) -> bool:
    print(f"  $ {' '.join(cmd)}")
    for attempt in range(1, retry + 1):
        if subprocess.run(cmd).returncode == 0:
            return True
        if attempt < retry:
            print(f"  [retry {attempt}/{retry}] failed, retrying...")
            time.sleep(2)
    return False


def _getvar(var: str) -> str:
    r = subprocess.run(["fastboot", "getvar", var],
                       capture_output=True, text=True)
    for line in (r.stdout + r.stderr).splitlines():
        if line.startswith(var + ":"):
            return line.split(":", 1)[1].strip()
    return ""


def _flash_partition_table(var: str, partition_json: str):
    size = _getvar(var)
    print(f"  [flash] {var} = {size!r}")
    if not size or size.lower() == "null":
        return False
    cfg = load_json(partition_json)
    fmt = cfg.get("format", "gpt")
    if not _run(["fastboot", "flash", fmt, partition_json], retry=3):
        return False
    for p in cfg["partitions"]:
        if not p.get("image"):
            continue
        f = TEMP_DIR / p["image"]
        if not f.exists():
            print(f"  [{p['name']}] no image, skipped")
            continue
        if not _run(["fastboot", "flash", p["name"], str(f)], retry=3):
            sys.exit(f"ERROR: flashing {p['name']} failed")
    return True


def fastboot():
    # FDL flow: BootROM -> FSBL -> full u-boot fastboot -> partitions
    print("[flash] looking for BootROM fastboot (version-brom)...")
    if _getvar("version-brom"):
        _run(["fastboot", "stage", str(TEMP_DIR / "FSBL.bin")], retry=3)
        _run(["fastboot", "continue"])
        time.sleep(10)
        _run(["fastboot", "oem", "speed:super-speed"])
    print("[flash] staging u-boot...")
    _run(["fastboot", "stage", str(TEMP_DIR / "u-boot.itb")], retry=3)
    _run(["fastboot", "continue"])
    time.sleep(10)
    if not _flash_partition_table("mtd-size", "partition_universal.json"):
        _flash_partition_table("blk-size", "partition_universal.json")
    print("[flash] done. Rebooting the board...")
    _run(["fastboot", "reboot"], retry=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--img", help="raw image to extract partitions from")
    ap.add_argument("--partition", default="partition_universal.json")
    ap.add_argument("--fastboot", action="store_true",
                    help="flash the board (assumes ./temp populated)")
    args = ap.parse_args()

    if not args.img and not args.fastboot:
        ap.error("either --img or --fastboot required")
    if args.img:
        extract(args.img, args.partition)
    if args.fastboot:
        fastboot()


if __name__ == "__main__":
    main()
