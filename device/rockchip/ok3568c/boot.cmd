setenv fdtfile "dtbs/rockchip/rk3568-ok3568c.dtb"

setenv bootargs "root=/dev/mmcblk1p2 rootwait rootfstype=ext4 splash=verbose console=ttyS2,1500000 console=tty1 consoleblank=0 loglevel=1 earlycon=uart8250,mmio32,0xfe660000 console=ttyFIQ0 cma=256M"

test -n "${distro_bootpart}" || distro_bootpart=1

echo "Boot script loaded from ${devtype} ${devnum}:${distro_bootpart}"

load ${devtype} ${devnum}:${distro_bootpart} ${ramdisk_addr_r} ${prefix}uInitrd
load ${devtype} ${devnum}:${distro_bootpart} ${kernel_addr_r} ${prefix}Image

load ${devtype} ${devnum}:${distro_bootpart} ${fdt_addr_r} ${prefix}${fdtfile}
fdt addr ${fdt_addr_r}
fdt resize 65536

printenv bootargs
printenv fdtfile
booti ${kernel_addr_r} ${ramdisk_addr_r} ${fdt_addr_r}

# Recompile with:
# mkimage -C none -A arm -T script -d /boot/boot.cmd /boot/boot.scr
