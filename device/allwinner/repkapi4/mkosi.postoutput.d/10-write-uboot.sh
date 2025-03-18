#!/bin/sh
# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
UBOOT_SPL="${SRCDIR}/u-boot-sunxi-with-spl.bin"

# Check if U-Boot SPL file exists
if [ ! -f "$UBOOT_SPL" ]; then
    printf "\n"
    printf "+-----------------------------+\n"
    printf "|       _                 _   |\n"
    printf "| _   _| |__   ___   ___ | |_ |\n"
    printf "|| | | | '_ \ / _ \ / _ \| __||\n"
    printf "|| |_| | |_) | (_) | (_) | |_ |\n"
    printf "| \__,_|_.__/ \___/ \___/ \__||\n"
    printf "+-----------------------------+\n"
    printf "\n"
    printf "  ⚠️  U-BOOT file u-boot-sunxi-with-spl.bin is missing!  ⚠️\n"
    printf "  Please compile U-Boot before running this script.\n"
    exit 0
fi

pushd "${OUTPUTDIR}"
printf "Writing bootloader to the image...\n"
dd if="${UBOOT_SPL}" of=image.raw bs=1k seek=128 conv=notrunc
popd
