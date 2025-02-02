#!/bin/bash
set -x

# Run mkosi with --force option
#mkosi --force

# Check if mkosi ran successfully
if [ $? -ne 0 ]; then
  printf "mkosi failed to execute.\n"
  exit 1
fi

# Calculate the size of the image directory
IMAGE_SIZE=$(du -sb ./image | cut -f1)
IMAGE_SIZE=$((IMAGE_SIZE + 256 * 1024 * 1024))  # Add 16 MB to the calculated size

# Create the orangepi5.img disk image with the calculated size
rm -fv orangepi5.img
dd if=/dev/zero of=orangepi5.img bs=1M count=0 seek=$((IMAGE_SIZE / 1024 / 1024))

# Attach the image to a loop device
LOOP_DEV=$(losetup --find --show orangepi5.img)

# Perform partitioning operations on the loop device
sgdisk --zap-all "${LOOP_DEV}"
sgdisk --new=1:16M:+0 --typecode=1:8305 "${LOOP_DEV}"

# Update the partition table
partprobe "${LOOP_DEV}"

# Create ext4 filesystem on the first partition
mkfs.ext4 -L rootfs "${LOOP_DEV}p1"

# Mount the first partition to a temporary directory
MOUNT_DIR=$(mktemp -d)
mount "${LOOP_DEV}p1" "$MOUNT_DIR"

# Copy the contents of the image directory to the first partition using rsync
rsync -a ./image/ "$MOUNT_DIR/"

# Unmount the partition
umount "$MOUNT_DIR"

# Remove the temporary mount directory
rmdir "$MOUNT_DIR"
# Print a success message
printf "Disk and partitions successfully created!\n"

printf "Write bootloader!\n"
dd if=idbloader.img of=${LOOP_DEV} seek=64 conv=notrunc
dd if=u-boot.itb of=${LOOP_DEV} seek=16384 conv=notrunc
