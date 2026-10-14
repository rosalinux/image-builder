# Milk-V Jupiter2 (SpacemiT K3, RISC-V64) — Rosa14 image

Bootable Rosa14 image for the Milk-V Jupiter2 board (SpacemiT K3 SoC).
The board boots **UEFI**: BootROM → FSBL → OpenSBI → EDK2 →
systemd-boot → Linux (kernel + initrd + devicetree from the ESP).

The layout mirrors the official
[K3-Ubuntu-Images](https://github.com/spacemit-com/K3-Ubuntu-Images)
(gpt offsets, FDL flash flow), but everything is built from source and
with mkosi instead of `ubuntu-image`:

| Component | Source |
|---|---|
| FSBL, bootinfo, env, u-boot.itb | `spacemit-com/uboot-2022.10`, branch `k3-br-v1.0.y`, `k3_defconfig` |
| fw_dynamic.itb (OpenSBI) | `spacemit-com/opensbi`, branch `k3-br-v1.0.y`, `PLATFORM=generic` + `k3_defconfig` |
| edk2.itb (UEFI) | `spacemit-com/edk2-spacemit`, `Platform/Spacemit/K3/MUSE-Pico` |
| kernel / rootfs | Rosa14 repos: `kernel-7.2-generic` (ships `spacemit/k3-pico-itx.dtb`) |

## Disk layout

```
0     .. 640K   (GPT + free)
640K  .. 768K   env        u-boot-env-default.bin
1M    .. 1152K  bootinfo   bootinfo_spinor.bin
1536K .. 2M     fsbl       FSBL.bin
7M    .. 8M     opensbi    fw_dynamic.itb
8M    .. 12M    uboot      edk2.itb
12M   .. 524M   ESP (/boot) vfat: vmlinuz, initrd, dtb,
                             EFI/BOOT/BOOTRISCV64.EFI (systemd-boot),
                             loader/entries/rosa.conf
524M  .. end    rootfs     ext4, label=rootfs
```

Firmware is written by `mkosi.postoutput.d/10-write-firmware.sh` at the
fixed offsets above (see `flash/partition_universal.json` for the same
table used by the flasher).

## Prerequisites

* GNU make, `mkosi` >= 24
* riscv64 cross toolchain (`make setup` in `u-boot/` installs it via dnf)
* `fastboot` on the host for flashing

## 1. Build firmware

```bash
cd u-boot/
make setup   # once: host build deps
make         # clone, patch, build, install artifacts into ../firmware/
```

Artifacts: `FSBL.bin`, `bootinfo_{spinor,spinand,block}.bin`,
`u-boot-env-default.bin`, `u-boot.itb`, `fw_dynamic.itb`, `edk2.itb`.

Notes baked into the Makefile:
* `SPL_SIZE_LIMIT` is raised to `0x78000` — the stock `0x72F00` assumes
  the SpacemiT vendor toolchain; gcc 14 emits ~1.5K more code, and the
  FSBL slot is 512K anyway.
* rosa multilib quirk: a 64-bit `libuuid.so` symlink is provided via
  `LIBRARY_PATH` for the EDK2 BaseTools build.

## 2. Build the image

```bash
cd ..                 # device/riscv64/jupiter2
mkosi --force
```

`mkosi` produces `image.raw` (GPT), populates the ESP by hand (no
mkosi `Bootable=`/UKI flow, as in napi2): `mkosi.postinst.chroot`
generates the dracut initrd, copies the devicetree, installs
systemd-boot as `EFI/BOOT/BOOTRISCV64.EFI` and writes the
`loader/entries/rosa.conf` type#1 entry (kernel, initrd, devicetree,
kernel command line). `mkosi.postoutput.d/10-write-firmware.sh` then
writes the firmware stages at their fixed offsets.

Result: `image.raw`, ready for `dd` or for the fastboot flow below.

## 3. Flash

The board is flashed over USB-C in the BootROM FDL mode, the same way
as the official Ubuntu images (own implementation in `flash/`, no
vendored code).

One-time host setup:

```bash
sudo dnf install fastboot
echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="361c", MODE="0666"' \
    | sudo tee /etc/udev/rules.d/51-spacemit.rules
sudo udevadm control --reload-rules && sudo udevadm trigger
```

Put the board into FDL mode:

1. **Press and hold** the FDL button
2. Briefly press **RST**
3. Release FDL
4. Check: `lsusb | grep -i spacemit` → "SpacemiT USB BOOT", and
   `fastboot devices` lists the board

Extract the partitions and flash:

```bash
cd flash/
make extract     # cut partitions out of ../image.raw into ./temp/
make flash       # FDL flow: stage FSBL -> u-boot -> flash table + partitions
# or both at once:
make all
```

## 4. Boot

Power-cycle the board. Expected on the serial console
(`console=ttyS0,115200` in the loader entry): OpenSBI banner, EDK2
UEFI, systemd-boot menu (3 s timeout), then the Rosa boot.

## Notes

* The devicetree is `spacemit/k3-pico-itx.dtb` from
  `kernel-7.2-generic`; alternatives shipped by the kernel:
  `k3-com260-ifx.dtb`, `k3-deepcomputing-fml13v05.dtb`. To change it,
  edit `mkosi.postinst.chroot` and rebuild the image.
* The `esos` firmware partition present in the Ubuntu layout is
  omitted; if a board revision turns out to require it, build it from
  `spacemit-com/esos` and add a partition at 4M.
* `K3-Ubuntu-Images/` is kept locally as an untracked reference clone.
