# Flash Instructions

## Prerequisites

- Device connected via USB-C (DRF Type-C port) to host
- `fastboot` and `adb` installed
- Extracted partitions in `temp/`

### USB Permissions (udev rule)

Without this, adb/fastboot will fail with `Access denied (insufficient permissions)`:

```bash
echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="361c", MODE="0666"' | sudo tee /etc/udev/rules.d/51-spacemit.rules
sudo udevadm control --reload-rules
sudo udevadm trigger
```

Then reconnect the USB cable or press RST on the board.

## Step 1: Extract Partitions

```bash
make IMG=ubuntu-26.04-preinstalled-desktop-riscv64.img.zst UBOOT_ITB=u-boot.itb extract
```

## Step 2: Enter FDL / Fastboot Mode

1. Connect the board to the host via USB-C cable
2. **Press and hold** the FDL button on the board
3. While holding FDL, **briefly press** the RST (reset) button
4. **Release** the FDL button
5. Verify the device is in fastboot mode:

```bash
lsusb | grep -i spacemit
# Should show "SpacemiT USB BOOT" (not "ADB device")

fastboot devices
# Should list the device serial number
```

## Step 3: Flash

```bash
make IMG=ubuntu-26.04-preinstalled-desktop-riscv64.img.zst UBOOT_ITB=u-boot.itb flash
```

Or extract + flash in one command:

```bash
make IMG=ubuntu-26.04-preinstalled-desktop-riscv64.img.zst UBOOT_ITB=u-boot.itb all
```

## References

- **SpacemiT K3 PPA (Launchpad):** https://launchpad.net/~spacemit/+archive/ubuntu/k3
- **PPA packages:** https://ppa.launchpadcontent.net/spacemit/k3/ubuntu
- **PPA sources:** https://ppa.launchpadcontent.net/spacemit/k3/ubuntu

## Troubleshooting

- **`< waiting for any device >`** — device is in ADB mode, not fastboot. Repeat Step 2 (FDL + RST).
- **`fastboot not in PATH`** — install: `sudo apt install fastboot`
- **`u-boot.itb not found`** — pass `UBOOT_ITB=u-boot.itb` or place the file at `workdir/scratch/gadget/install/u-boot-spacemit/u-boot.itb`
- **`Access denied (insufficient permissions)`** — add udev rule (see Prerequisites above)
- **Device shows as ADB** — switch to fastboot with `adb reboot bootloader` or use FDL + RST procedure
