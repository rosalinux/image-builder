#!/bin/sh
#set -x
#env
## SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
#UBOOT_DIR="${SRCDIR}/mkosi"
#
#IMAGE="${OUTPUTDIR}/orangepi5.img"
#IMAGE_SIZE=$(du -sb "${OUTPUTDIR}/image" | cut -f1)
#IMAGE_SIZE=$((IMAGE_SIZE + 15 * 1024 * 1024))
#
#dd if=/dev/zero of="${IMAGE}" bs=1M count=0 seek=$((IMAGE_SIZE / 1024 / 1024))
#
#LOOP_DEV=$(losetup --find --show "${IMAGE}")
#
#sgdisk --zap-all "${LOOP_DEV}"
#sgdisk --new=1:15M:+256M --typecode=1:8300 "${LOOP_DEV}"
#sgdisk --new=2:0:0 --typecode=2:8300 "${LOOP_DEV}"
#
#partprobe "${LOOP_DEV}"
#
#printf "Disk created!\n"
#
#pushd ${OUTPUTDIR}
#ls -la
#printf "write bootloader to the image...\n"
#dd if=${UBOOT_DIR}/idbloader.img of=${IMAGE} seek=64 conv=notrunc
#dd if=${UBOOT_DIR}/u-boot.itb of=${IMAGE} seek=16384 conv=notrunc
#popd
