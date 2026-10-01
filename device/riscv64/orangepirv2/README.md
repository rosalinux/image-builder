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

## Updating the Bootloader in SPI NOR Flash

The board boots its bootloader from the 16 MiB SPI NOR flash (`XM25QU128C`)
when no SD card is present. Kernel and rootfs are loaded from NVMe.

NOR layout (matches the SPL default `MTDPARTS_DEFAULT`):

| Offset      | Size    | Partition | Contents |
|-------------|---------|-----------|----------|
| `0x00000`   | 64K     | bootinfo  | vendor ROM boot info — **do not touch** |
| `0x10000`   | 64K     | private   | (unused) |
| `0x20000`   | 256K    | fsbl      | `FSBL.bin` |
| `0x60000`   | 64K     | env       | erased; U-Boot env comes from bootfs (`env_k1-x.txt`) |
| `0x70000`   | 192K    | opensbi   | unused (OpenSBI is embedded in `u-boot.itb`) |
| `0xa0000`   | ~14M    | uboot     | `u-boot.itb` |

### 1. Put the new files on the SD card

Copy the freshly built artifacts to the bootfs partition (partition 2) of
the SD card:

```bash
sudo mount /dev/<sd>2 /mnt
sudo cp FSBL.bin u-boot.itb /mnt/
sync && sudo umount /mnt
```

Insert the SD card and press reset: the ROM loads the bootloader from the
SD card (SD is always tried first), interrupt autoboot to get the `=>` prompt.

### 2. Flash from the U-Boot console

```text
# load images into RAM
load mmc 0:2 0x20000000 FSBL.bin
load mmc 0:2 0x24000000 u-boot.itb
echo FSBL=${filesize}          # note it: this is the itb size, FSBL was first

# FSBL @ 0x20000 (size 0x30720 = 198240 for the current build)
sf probe
sf erase 0x20000 0x40000
sf write 0x20000000 0x20000 0x30720
sf read 0x26000000 0x20000 0x30720
cmp.b 0x20000000 0x26000000 0x30720

# U-Boot + OpenSBI FIT @ 0xa0000 (size 0x2a0925 = 2754853 for the current build)
sf erase 0xa0000 0x2b0000
sf write 0x24000000 0xa0000 0x2a0925
sf read 0x2a000000 0xa0000 0x2a0925
cmp.b 0x24000000 0x2a000000 0x2a0925
```

Adjust the sizes to the actual `stat -c %s FSBL.bin u-boot.itb` values of
your build (use hex in the console). Each `cmp.b` must print
`Total of N byte(s) were the same`.

### 3. Test

Remove the SD card and press reset. Expected on the serial console
(115200 8N1):

```text
bm:3 (SD absent) -> bm:4 (NOR)
U-Boot SPL 2022.10 ...          # your build
Boot from fit configuration x1_orangepi-rv2
OpenSBI v1.9
U-Boot 2022.10 ...              # then PCIe/NVMe scan, systemd-boot, kernel
```

### Notes

* If a bad FSBL is flashed, the ROM falls through to USB download mode
  (`Switch to download device`). Recovery: insert the SD card and press
  reset — the ROM always tries SD first — then re-flash.
* The ROM verifies the FSBL signature; images built from the `k1-bl-v2.2.10`
  tree with the stock `board/spacemit/k1-x/configs/key/` keys are accepted.
* A known-good prebuilt FSBL (built by Alpine's native riscv64 toolchain)
  is available in the Alpine `u-boot-spacemit` APK if a locally built FSBL
  misbehaves in NOR (symptom: `fit_find_config_node: Missing FDT description`
  although the image verifies fine on flash).

## License

This project is released under the MIT License.
