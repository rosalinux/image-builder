#!/bin/sh
# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
set -x
UBOOT_DIR="${SRCDIR}/mkosi"

env
pushd ${OUTPUTDIR}
printf "write bootloader to the image...\n"
ls -la ../src/
#dd if=${UBOOT_DIR}/idbloader.img of=image.raw seek=64 conv=notrunc
#dd if=${UBOOT_DIR}/u-boot.itb of=image.raw seek=16384 conv=notrunc
popd
