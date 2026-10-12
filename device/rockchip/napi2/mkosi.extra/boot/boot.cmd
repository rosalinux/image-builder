setenv fdtfile "dtbs/rockchip/rk3568-napi-2.dtb"
setenv bootargs "root=LABEL=rootfs rw rootwait rootfstype=ext4 console=ttyS2,1500000 console=tty1 consoleblank=0 loglevel=7 earlycon=uart8250,mmio32,0xfe660000 cma=256M audit=0"
setenv distro_bootpart 2
echo "Boot script loaded from ${devtype} ${devnum}:${distro_bootpart}"
load ${devtype} ${devnum}:${distro_bootpart} ${ramdisk_addr_r} ${prefix}INITRD_REPLACE
load ${devtype} ${devnum}:${distro_bootpart} ${kernel_addr_r} ${prefix}IMAGE_REPLACE
load ${devtype} ${devnum}:${distro_bootpart} ${fdt_addr_r} ${prefix}${fdtfile}
fdt addr ${fdt_addr_r}
fdt resize 65536
printenv bootargs
printenv fdtfile
booti ${kernel_addr_r} ${ramdisk_addr_r} ${fdt_addr_r}
# Recompile with:
# mkimage -C none -A arm -T script -d /boot/boot.cmd /boot/boot.scr
