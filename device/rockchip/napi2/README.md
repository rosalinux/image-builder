# NAPI2 (Rockchip RK3568J) — Rosa13 image

Build instructions for a bootable Rosa13 SD image for the
[Napilab NAPI2](https://napiworld.ru/docs/computers/napi2/) board
(RK3568J, 4 GiB LPDDR4, 32 GiB eMMC, 2x GbE, USB3, HDMI).

The bootloader chain and the image are built separately:

1. **U-Boot** is built by hand with `u-boot/Makefile` (as in
   `device/riscv64/orangepirv2`), which drops the artifacts into this
   directory.
2. **The image** is then produced by plain `mkosi --force`, which
   installs packages from the Rosa13 repos and writes the bootloader
   into the raw image.

## Prerequisites

* GNU make, `mkosi` >= 24
* aarch64 cross toolchain and host build tools
  (`make setup` in `u-boot/` installs them via dnf)

## 1. Build U-Boot

```bash
cd u-boot/
make setup   # once: install host build deps
make         # clone, patch, build, install artifacts into ../
```

By default it builds **mainline U-Boot v2025.07** with a NAPI2 board
port (dts + defconfig patch in `patches-mainline/`, ported from the
vendor kernel dts; includes RK809 PMIC support required for SD-card
power) plus rkbin blobs (`rk3568_ddr_1560MHz_v1.21.bin`,
`rk3568_bl31_v1.44.elf`).

The radxa vendor tree is kept as a fallback flavor:

```bash
make FLAVOR=vendor   # radxa next-dev-v2024.10 (2017.09 base) + lab240 patches
```

Resulting artifacts (copied to the device directory):

| File           | Contents                          | Written at |
|----------------|-----------------------------------|------------|
| `idbloader.img`| DDR init blob + SPL               | sector 64  |
| `u-boot.itb`   | U-Boot proper + BL31 (TF-A) FIT   | sector 16384 |

## 2. Build the image

```bash
cd ..      # device/rockchip/napi2
mkosi --force
```

This assembles `image.raw` (GPT: 15M bootloader gap, 256M vfat `/boot`,
ext4 rootfs labeled `rootfs`), generates `boot.scr` from
`mkosi.extra/boot/boot.cmd` and finally writes the bootloader
artifacts with `mkosi.postoutput.d/10-dd-loader.sh`.

The image relies on `kernel-6.18-rockchip` from the Rosa repos; the
package must ship the `rk3568-napi-2.dtb` device tree and RK808/RK809
PMIC support (`CONFIG_MFD_RK8XX_I2C`, `CONFIG_REGULATOR_RK808`,
`CONFIG_COMMON_CLK_RK808`, `CONFIG_RTC_DRV_RK808`) — without the PMIC
driver both MMC controllers and both ethernet MACs stay in deferred
probe forever.

## 3. Flash and boot

```bash
dd if=image.raw of=/dev/sdX bs=1M && sync
```

Serial console: **UART2, 1500000 8N1**. Expected boot log:

```
DDR ... v1.21
U-Boot SPL 2025.07 ...
U-Boot 2025.07 ...
Model: Napilab NAPI2
PMIC:  RK809
...
Boot script loaded from mmc 1:2      # boot.scr from the /boot partition
```

Root login is available on the serial console (see `RootPassword` in
`mkosi.conf`) and on tty1.

## Recovery

If the SD card is not bootable, the BootROM falls into MASKROM mode;
`rkdeveloptool` can then write the images directly:

```bash
rkdeveloptool db  rk356x_spl_loader_ddr1056_v1.12.109_no_check_todly.bin
rkdeveloptool wl 64      idbloader.img
rkdeveloptool wl 16384   u-boot.itb
```

(The loader binary is kept out of git — grab it from the rkbin repo.)

## Notes

* Display output: the HDMI pipeline (VOP2 -> dw-hdmi) works up to an
  active 1920x1080@60 mode with the mainline stack; the bundled
  front-panel display of the HDMI kit variant is driven through an
  internal HDMI->scaler board. The vendor images additionally use a
  Rockchip BSP dw-hdmi driver (`rockchip,phy-table`) — port it only if
  a replacement display turns out to be picky about the mainline PHY
  programming.
* The `nnz` kernel tree with vendor LVDS support lives at
  gitlab.nnz-ipc.net/pub/napilinux/kernel (branch `linux-6.18.y`).
