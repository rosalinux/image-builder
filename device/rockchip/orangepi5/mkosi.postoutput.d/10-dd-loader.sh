#!/bin/sh
# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
set -Eeuo pipefail

UBOOT_DIR="${SRCDIR}/mkosi"
IMAGE="${OUTPUTDIR}/image.raw"

pushd ${OUTPUTDIR}
printf "write bootloader to the image...\n"
dd if=${UBOOT_DIR}/idbloader.img of=${IMAGE} seek=64 conv=notrunc
dd if=${UBOOT_DIR}/u-boot.itb of=${IMAGE} seek=16384 conv=notrunc
popd
