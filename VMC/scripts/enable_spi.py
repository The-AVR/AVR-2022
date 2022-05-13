#!/usr/bin/env python3

# Reverse-engineered from /opt/nvidia/jetson-io/jetson-io.py

from Jetson import board

header = "Jetson 40pin Header"
pin_group = "spi1"

jetson = board.Board()

# this is required to create the .header class attribute
jetson.set_active_header(header)

if not jetson.header.pingroup_is_enabled(pin_group):
    print(f"Enabling {pin_group} pin group")

    jetson.header.pingroup_enable(pin_group)
    dtbo = jetson.create_dtbo_for_header()
    dtb = jetson.create_dtb_for_headers([dtbo])

    print(f"Device Tree Boot {dtb} generated")

else:
    print(f"Pin group {pin_group} already enabled")
