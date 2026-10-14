#!/bin/sh
# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
IDBLOADER="${SRCDIR}/idbloader.img"
UBOOT_ITB="${SRCDIR}/u-boot.itb"

if [ ! -f "$IDBLOADER" ] || [ ! -f "$UBOOT_ITB" ]; then
    printf "\n"
    printf "+--------------------------------------+\n"
    printf "|  u-boot artifacts are missing!       |\n"
    printf "|  run 'make' in u-boot/ before mkosi  |\n"
    printf "+--------------------------------------+\n"
    printf "\n"
    exit 0
fi

pushd "${OUTPUTDIR}"
printf "Writing bootloader to the image...\n"
dd if=${IDBLOADER} of=image.raw seek=64 conv=notrunc
dd if=${UBOOT_ITB} of=image.raw seek=16384 conv=notrunc
popd
