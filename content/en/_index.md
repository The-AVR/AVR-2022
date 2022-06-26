---
title: "Bell AVR"

cascade:
  - type: "docs"
---

## Introduction

Welcome to the documentation for the Bell Vertical Robotics Competition!
Be sure to pay attention to the navigation links on the left and please keep in mind
that this documentation is a **living document** that will be constantly updated over time.
There will be new sections added, typos fixed, and bugs squashed throughout
this process.

{{% alert title="Warning" color="warning" %}}
It is **incredibly important** to follow the steps outlined in this documentation in
order. The navigation on the left provides a sequential ordering of steps.
{{% /alert %}}

## Requirements

To be able to successfully compete in AVR, you must have the following
available to you:

- A 3D printer (8.5" cubed) with 1 roll of ABS filament
- A laptop with one of the following:
  - Windows 10/11 with admin privileges
  - MacOS TODO
  - Debian-based Linux (Ubuntu, Pop!\_OS, Mint, etc) with `sudo` privileges
- Basic shop tools and supplies:
  - Zip ties
  - Soldering iron
  - Screwdrivers
  - etc.

## Prerequisites

For AVR, you'll need to 3D print some parts for your drone.
While not needed immediately, these are good to get started with:

- [Landing gear](https://github.com/bellflight/AVR-2022/blob/main/3DPrints/Misc/Drone_Landing_Spike.STL) (x4)
  - Estimated print time: 1 hour 20 minutes per leg
- [VMC mounting blocks](https://github.com/bellflight/AVR-2022/blob/main/3DPrints/JetsonNano/Jetson_Blocks.STL) (x2)
  - Estimated print time: 52 minutes per block
- [VMC mounting case](https://github.com/bellflight/AVR-2022/blob/main/3DPrints/JetsonNano/Jetson_Mount_Cooling.STL)
  - Estimated print time: 2 hours 10 minutes
- [VMC Wi-Fi antenna mount](https://github.com/bellflight/AVR-2022/blob/main/3DPrints/Misc/Wifi_Antenna_Mount.STL) (x2)
  - Estimated print time: 1 hour 15 minutes per print
  - The additional print will be used for mounting your PCC
- [T-265 mount](https://github.com/bellflight/AVR-2022/blob/main/3DPrints/Misc/T265_Rail_Mount.STL)
  - Estimated print time: 1 hour 30 minutes

While you are free to design your own rotor guards, a premade design is available
with some extra hardware that will be need to be purchased seperately:

- [Rotor guards](https://github.com/bellflight/AVR-2022/tree/main/3DPrints/PropGuards) (x4)
  - Estimated print time: 2 hours 30 minutes per motor
- 3 x [10-Pack of Aluminum Standoffs (80mm)](https://www.amazon.com/uxcell-Aluminum-Standoff-Fastener-Quadcopter/dp/B01MSAHZQO/)
- 1 x [100-Pack of 14mm Long M3 Screws](https://www.amazon.com/M3x14mm-Screw-Socket-Screws-100Pcs/dp/B0143GZU4W/)
