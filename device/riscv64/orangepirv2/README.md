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

Navigate to the `u-boot` directory and run:

```bash
cd u-boot/
make
cd -
```

### 2. Copy Required Firmware Files

After building, copy the following files:

```
u-boot/u-boot-orangepi/FSBL.bin  
u-boot/u-boot-orangepi/bootinfo_sd.bin  
u-boot/u-boot-orangepi/u-boot.itb  
u-boot/pi-opensbi/build/platform/generic/firmware/fw_dynamic.itb
```

into the directory where your `mkosi.conf` file is located.

### 3. Build Image with mkosi

Run the following command to generate the final firmware image:

```bash
mkosi --force
```

This will produce a bootable image that can be written to an SD card for the Orange Pi RV2.

## Notes

* Ensure all build dependencies are installed.
* You may need to configure `mkosi.conf` for your target distribution and architecture (e.g., `riscv64`).
* Tested on Orange Pi RV2 with \[insert tested distribution, e.g. Debian, Fedora].

## License

This project is released under the MIT License.
