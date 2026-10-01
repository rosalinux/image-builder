<img width="793" alt="Снимок экрана 2025-05-07 в 01 15 13" src="https://github.com/user-attachments/assets/35d1bc8b-2f3b-42e7-aeed-e16616fd5315" />

# Firmware Build Instructions for Orange Pi RV2 (RISC-V64)

This guide explains how to build a bootable firmware image for the Orange Pi RV2 board using `u-boot`, `OpenSBI`, and `mkosi`.

## Prerequisites

* GNU Make
* mkosi ([https://github.com/systemd/mkosi](https://github.com/systemd/mkosi))
* RISC-V64 cross-toolchain
* u-boot source code with Orange Pi patches
* OpenSBI source code

## Build Steps

### 1. Build U-Boot

The build follows the Alpine Linux `aports/testing/u-boot-spacemit` recipe:
official SpacemiT U-Boot fork (`k1-bl-v2.2.10-release`) with aports patches,
plus mainline OpenSBI embedded into `u-boot.itb` (no separate `fw_dynamic.itb`).

Navigate to the `u-boot` directory and run:

```bash
cd u-boot/
make setup   # once: install host build deps
make         # clone, patch, build, install artifacts into ../
cd -
```

### 2. Firmware Files

`make` (target `install`) copies the required files into this directory:

```
FSBL.bin               # SPL, written at sector 256
bootinfo_sd.bin        # boot info, written at sector 0
u-boot.itb             # U-Boot + embedded OpenSBI, written at sector 2048
u-boot-env-default.bin # reference default environment
```

### 3. Build Image with mkosi

Run the following command to generate the final firmware image:

```bash
mkosi --force
```

This will produce a bootable image that can be written to an SD card for the Orange Pi RV2.

```bash
dd if=image.raw of=/dev/your_sd_card bs=1M;sync
```

## Manual Boot from MMC (U-Boot console)

Interrupt autoboot (press any key during the countdown), then load the
kernel, initramfs and DTB from the bootfs partition (partition 2 on the
boot device; SD is `mmc 0` on this board) and boot with `booti`:

```
load mmc 0:2 ${kernel_addr_r} vmlinuz-<version>
load mmc 0:2 ${fdt_addr_r} dtb-<version>/spacemit/k1-orangepi-rv2.dtb
load mmc 0:2 ${ramdisk_addr_r} initramfs-<version>.img
setenv initrd_size ${filesize}
setenv bootargs "root=PARTUUID=<root-partuuid> rootwait rw console=ttyS0,115200 loglevel=7 earlycon=sbi"
booti ${kernel_addr_r} ${ramdisk_addr_r}:${initrd_size} ${fdt_addr_r}
```

Replace `<version>` with the kernel release (e.g. `7.2.8-generic-1rosa14-riscv64`)
and `<root-partuuid>` with the PARTUUID of the rootfs partition
(`lsblk -o NAME,PARTUUID` or `blkid` on the host; it is also printed by
U-Boot's `part list mmc 0`). Booting without an initramfs is possible too
(pass `-` instead of the ramdisk argument) — useful for bring-up, since
the console drivers are built into the kernel.

### Debug variants

If the kernel produces no output, use the raw MMIO earlycon (works
independently of DT/clock setup, UART0 on K1 is at 0xd4017000):

```
setenv bootargs "root=PARTUUID=<root-partuuid> rootwait rw earlycon=uart8250,mmio32,0xd4017000,115200n8 console=ttyS0,115200n8 loglevel=8 ignore_loglevel keep_bootcon"
```

Check what U-Boot passed to the kernel:

```
fdt addr ${fdt_addr_r}
fdt print /chosen        # bootargs, stdout-path, initrd info
fdt print /aliases       # serial0 alias -> uart node
```

## License

This project is released under the MIT License.
