#!/bin/sh
# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
BOOTINFO_SD="${SRCDIR}/bootinfo_sd.bin"
FSBL="${SRCDIR}/FSBL.bin"
FW_OPENSBI="${SRCDIR}/fw_dynamic.itb"
OPENSBI="${SRCDIR}/u-boot.itb"

# Check if U-Boot SPL file exists
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
    exit 0
fi

pushd "${OUTPUTDIR}"
printf "Writing bootloader to the image...\n"
dd if=${BOOTINFO_SD} of=image.raw seek=0 conv=notrunc
dd if=${FSBL} of=image.raw seek=256 conv=notrunc
dd if=${FW_OPENSBI} of=image.raw seek=1280 conv=notrunc
dd if=${OPENSBI} of=image.raw bs=512 seek=2048 conv=notrunc
popd
