#!/bin/sh
# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# Write the SpacemiT K3 firmware stages into the raw image, below the ESP.
# Offsets follow the K3-Ubuntu-Images partition_universal.json layout
# (sd-boot/ESP starts at 12M, see mkosi.repart/10-esp.conf).
set -Eeuo pipefail

FW="${SRCDIR}/firmware"
IMAGE="${OUTPUTDIR}/image.raw"

MISSING=0
for f in u-boot-env-default.bin bootinfo_spinor.bin FSBL.bin fw_dynamic.itb edk2.itb; do
	if [ ! -f "${FW}/${f}" ]; then
		printf "  MISSING: firmware/%s (run 'make' in u-boot/)\n" "${f}"
		MISSING=1
	fi
done
if [ "${MISSING}" = 1 ]; then
	printf "+--------------------------------------+\n"
	printf "|  K3 firmware artifacts are missing!  |\n"
	printf "|  run 'make' in u-boot/ before mkosi  |\n"
	printf "+--------------------------------------+\n"
	exit 0
fi

pushd "${OUTPUTDIR}"
printf "Writing K3 firmware...\n"
dd if=${FW}/u-boot-env-default.bin of=${IMAGE} bs=512 seek=1280  conv=notrunc   # env      @ 640K
dd if=${FW}/bootinfo_spinor.bin    of=${IMAGE} bs=512 seek=2048  conv=notrunc   # bootinfo @ 1M
dd if=${FW}/FSBL.bin               of=${IMAGE} bs=512 seek=3072  conv=notrunc   # fsbl     @ 1536K
dd if=${FW}/fw_dynamic.itb         of=${IMAGE} bs=512 seek=14336 conv=notrunc   # opensbi  @ 7M
dd if=${FW}/edk2.itb               of=${IMAGE} bs=512 seek=16384 conv=notrunc   # uboot    @ 8M
popd
