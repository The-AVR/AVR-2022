---
title: "Advanced VRC Drone Assembly"
weight: 9
---

Please make sure you've successfully **built** and **flown** your basic VRC drone.
You will be making some extensive modifications to your drone in
preparation for advanced assembly.

The modifications for advanced assembly will require some disassembly and the following
additions to your drone:

- **3D printed components**
  - For mounting various cameras and peripherals
- **Vehicle Management Computer (VMC)**
  - Runs VRC code
  - Interfaces with external sensors
  - Provides wireless interface with PX4
- **Camera Serial Interface (CSI)**
  - Downward facing camera
  - For April Tag detection
- **Intel T-265 Tracking Camera**
  - For real-time mapping of the environment
  - For position hold
- **FPV Projection Camera**
  - For a live feed of the game court
- **Peripheral Control Computer (PCC)**
  - For LED and servo actuation

![Block Diagram for the Advanced Drone](phaseI-II.drawio.png)

Please make sure to 3D print the following parts before beginning your
advanced drone modifications. These are necessary to complete advanced assembly
and prepare for competition day.

- [Landing gear](https://github.com/bellflight/VRC-2022/blob/main/3DPrints/Misc/Drone_Landing_Spike.STL) (x4)
  - Estimated print time: 1 hour 20 minutes per leg
- [VMC mounting blocks](https://github.com/bellflight/VRC-2022/blob/main/3DPrints/JetsonNano/Jetson_Blocks.STL) (x2)
  - Estimated print time: 52 minutes per block
- [VMC mounting case](https://github.com/bellflight/VRC-2022/blob/main/3DPrints/JetsonNano/Jetson_Mount_Cooling.STL)
  - Estimated print time: 2 hours 10 minutes
- [VMC Wi-Fi antenna mount](https://github.com/bellflight/VRC-2022/blob/main/3DPrints/Misc/Wifi_Antenna_Mount.STL) (x2)
  - Estimated print time: 1 hour 15 minutes per print
  - The additional print will be used for mounting your PCC
- [T-265 mount](https://github.com/bellflight/VRC-2022/blob/main/3DPrints/Misc/T265_Rail_Mount.STL)
  - Estimated print time: 1 hour 30 minutes
- [Rotor guards](https://github.com/bellflight/VRC-2022/tree/main/3DPrints/PropGuards) (x4)
  - Estimated print time: 2 hours 30 minutes per motor
