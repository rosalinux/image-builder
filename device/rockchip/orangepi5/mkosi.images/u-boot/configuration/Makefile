FILES = \
    rk3588s-orangepi-5-sata.dts \
    rk3588s-orangepi-5.dts \
    rk3588s-orangepi-5b.dts \
    orangepi-5-rk3588s_defconfig

URL_BASE = https://github.com/armbian/build/raw/refs/heads/main/patch/u-boot/legacy/u-boot-radxa-rk35xx

all: $(FILES)

rk3588s-orangepi-5-sata.dts:
	wget $(URL_BASE)/dt/$@

rk3588s-orangepi-5.dts:
	wget $(URL_BASE)/dt/$@

rk3588s-orangepi-5b.dts:
	wget $(URL_BASE)/dt/$@

orangepi-5-rk3588s_defconfig:
	wget $(URL_BASE)/defconfig/$@

clean:
	rm -f $(FILES)
