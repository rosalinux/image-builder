#!/bin/bash
# Find vmlinuz and initrd files in the /boot directory
vmlinuz_file=$(find ${BUILDROOT}/boot -name 'vmlinuz-*' -type f | head -n 1)
initrd_file=$(find ${BUILDROOT}/boot -name 'initrd-*.img' -type f | head -n 1)

# Check if both files were found
if [[ -z "$vmlinuz_file" || -z "$initrd_file" ]]; then
    printf "Error: vmlinuz or initrd files not found in /boot.\n"
    exit 1
fi

# Extract the base names of the files (without the directory path)
kernel_name=$(basename "$vmlinuz_file")
initrd_name=$(basename "$initrd_file")

# Append the required lines to /boot/config.txt
{
    printf "kernel=%s\n" "$kernel_name"
    printf "initramfs %s followkernel\n" "$initrd_name"
} >> ${BUILDROOT}/boot/config.txt

printf "The kernel and initrd entries have been added to /boot/config.txt.\n"
