# Flash Instructions (Rosa14)

## Prerequisites

- Device connected via USB-C to the host
- `fastboot` installed (`sudo dnf install fastboot`)

### USB Permissions (udev rule)

```bash
echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="361c", MODE="0666"' | sudo tee /etc/udev/rules.d/51-spacemit.rules
sudo udevadm control --reload-rules
sudo udevadm trigger
```

Reconnect the USB cable afterwards.

## Build the image first

From the device directory:

```bash
cd u-boot && make setup && make    # K3 firmware (FSBL, opensbi, edk2)
cd .. && mkosi --force             # image.raw with firmware + sd-boot ESP
```

## Step 1: Extract Partitions

```bash
cd flash
make extract
```

## Step 2: Enter FDL / Fastboot Mode

1. Connect the board via USB-C
2. **Press and hold** the FDL button
3. While holding FDL, briefly press **RST**
4. Release FDL
5. Verify:

```bash
lsusb | grep -i spacemit     # "SpacemiT USB BOOT"
fastboot devices
```

## Step 3: Flash

```bash
make flash        # or: make all  (extract + flash)
```

The flow stages FSBL into the BootROM, then u-boot into RAM, then
flashes the GPT partition table (`partition_universal.json`) and every
partition from `temp/`.

## Boot

Power-cycle the board. Boot chain: BootROM -> FSBL -> OpenSBI ->
EDK2 (UEFI) -> systemd-boot (`EFI/BOOT/BOOTRISCV64.EFI`) ->
loader entry `rosa.conf` (kernel + initrd + `k3-pico-itx.dtb`).

Serial console: check the board documentation; the loader entry uses
`console=ttyS0,115200`.
