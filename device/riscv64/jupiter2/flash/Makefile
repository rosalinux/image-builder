# Flash Rosa14 to a SpacemiT K3 board (Milk-V Jupiter2) via fastboot.
#
#   make extract   # cut partitions out of ../image.raw into ./temp
#   make flash     # FDL flow + flash all partitions
#   make all       # extract + flash
#
# Board must be in FDL mode: hold FDL, press RST, release FDL
# (`lsusb | grep -i spacemit` should show "SpacemiT USB BOOT").
#
# USB permissions (one-time):
#   echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="361c", MODE="0666"' \
#       | sudo tee /etc/udev/rules.d/51-spacemit.rules
#   sudo udevadm control --reload-rules && sudo udevadm trigger

PYTHON  ?= python3
SCRIPT  ?= image_flash.py
PARTITION ?= partition_universal.json
IMG     ?= ../image.raw

.PHONY: all extract flash

all: extract flash

extract: $(IMG) $(PARTITION)
	$(PYTHON) $(SCRIPT) --img $(IMG) --partition $(PARTITION)

flash:
	sudo $(PYTHON) $(SCRIPT) --fastboot
