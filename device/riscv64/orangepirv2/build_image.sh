#!/bin/bash
set -euo pipefail

# === Colors ===
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# === Constants ===
IMAGE_NAME="orangep_rv2_rosa13.image"
IMAGE_DIR="./image"
MOUNT_POINT="/mnt/image_mount"
MIN_EXTRA_MB=100
PARTITION_OFFSET_MB=30

# Bootloader files
BOOTINFO_SD="bootinfo_sd.bin"
FSBL="FSBL.bin"
UBOOT_ENV="u-boot-env-default.bin"
OPENSBI="u-boot-opensbi.itb"

green() {
    echo -e "${GREEN}[+] $*${NC}"
}

# === Ensure required tools are available ===
for cmd in mkosi losetup parted blockdev mkfs.ext4 rsync; do
    command -v $cmd >/dev/null 2>&1 || {
        echo "Required command '$cmd' is not installed."
        exit 1
    }
done

# === Step 1: Build image using mkosi ===
green "[+] Running mkosi clean..."
#mkosi clean
green "[+] Running mkosi --force..."
#mkosi --force

# === Step 2: Calculate size of the image directory ===
if [[ ! -d "$IMAGE_DIR" ]]; then
    echo "Directory $IMAGE_DIR not found."
    exit 1
fi

green "[+] Calculating size of $IMAGE_DIR..."
DIR_MB=$(du -sm "$IMAGE_DIR" | cut -f1)
TOTAL_MB=$((DIR_MB + MIN_EXTRA_MB))
green "[+] Target image size: $TOTAL_MB MB"

# === Step 3: Create empty image file ===
green "[+] Creating image file $IMAGE_NAME..."
fallocate -l "${TOTAL_MB}M" "$IMAGE_NAME"

# === Step 4: Associate loop device ===
green "[+] Attaching loop device..."
LOOP_DEV=$(losetup --show -fP "$IMAGE_NAME")
green "[+] Loop device: $LOOP_DEV"

# === Step 5: Create DOS (MBR) partition table ===
green "[+] Creating DOS (MBR) partition table..."
dd if=/dev/zero of="$LOOP_DEV" bs=512 count=1
parted -s "$LOOP_DEV" mklabel msdos
parted -s "$LOOP_DEV" mkpart primary ext4 ${PARTITION_OFFSET_MB}MiB 100%

# === Step 6: Wait for /dev/loopXp1 to appear ===
PARTITION_DEV="${LOOP_DEV}p1"
for i in {1..10}; do
    if [[ -b "$PARTITION_DEV" ]]; then
        break
    fi
    green "[!] Waiting for partition device $PARTITION_DEV to appear..."
    sleep 0.5
done

if [[ ! -b "$PARTITION_DEV" ]]; then
    green "Partition device $PARTITION_DEV not found."
    losetup -d "$LOOP_DEV"
    exit 1
fi

# === Step 7: Format partition as ext4 ===
green "[+] Formatting $PARTITION_DEV as ext4..."
mkfs.ext4 -F "$PARTITION_DEV"

# === Step 8: Mount partition ===
green "[+] Mounting partition to $MOUNT_POINT..."
mkdir -p "$MOUNT_POINT"
mount "$PARTITION_DEV" "$MOUNT_POINT"

# === Step 9: Copy content from image directory ===
green "[+] Copying files to mounted partition..."
rsync -aHAX "$IMAGE_DIR"/ "$MOUNT_POINT"/

# === Step 10: Write bootloader if available ===
if [ ! -f "$BOOTINFO_SD" ]; then
    printf "\n"
    printf "+-----------------------------+\n"
    printf "|       _                 _   |\n"
    printf "| _   _| |__   ___   ___ | |_ |\n"
    printf "|| | | | '_ \ / _ \ / _ \| __||\n"
    printf "|| |_| | |_) | (_) | (_) | |_ |\n"
    printf "| \__,_|_.__/ \___/ \___/ \__||\n"
    printf "+-----------------------------+\n"
    printf "\n"
    printf "  ⚠️  U-BOOT filepart bootinfo_sd.bin is missing!  ⚠️\n"
    printf "  Please compile bootloader before running this script.\n"
    printf "\n"
fi

if [ -f "$BOOTINFO_SD" ]; then
    green "[+] Writing bootloader files to ${LOOP_DEV}..."
    dd if=${BOOTINFO_SD} of=${LOOP_DEV} seek=0 conv=notrunc status=none
    dd if=${FSBL} of=${LOOP_DEV} seek=256 conv=notrunc status=none
    dd if=${UBOOT_ENV} of=${LOOP_DEV} seek=768 conv=notrunc status=none
    dd if=${OPENSBI} of=${LOOP_DEV} seek=1664 conv=notrunc status=none
fi

# === Step 11: Cleanup ===
green "[+] Syncing and unmounting..."
sync
umount "$MOUNT_POINT"
losetup -d "$LOOP_DEV"

green "[✓] Image $IMAGE_NAME created, formatted and populated successfully."
