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
dd if=image of=/dev/your_sd_card bs=1M;sync
```

## License

This project is released under the MIT License.
