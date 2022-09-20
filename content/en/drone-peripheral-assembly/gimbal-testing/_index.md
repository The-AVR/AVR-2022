---
title: "Gimbal Testing"
weight: 2
---

## Gimbal

Make sure your jetson is up to date

Tested in previous version but we can do it again here

Start the docker container that houses all the code for the pcc container as well as mqtt for so we can connect and send/receive messages from the GUI

Connect to your jetson using your preferred method. Then run the following:

```bash
cd AVR-2022/VMC/
./start.py run mqtt pcc
```

Connect your GUI (need your jetson IP for this)

Navigate to the thermal view tab

Move your joystick and ensure the gimbal moves appropriately.

## Laser pointer

Press the fire button and ensure the laser fires

Press the laser on and ensure that the laser pulses, this mode can be used as an indicator light for ensuring you are pointing at your hotspot.

Ensure the laser turns off.

## Thermal Camera

The thermal camera should have a green light on the camera if it receives power.

After powering on your drone, ensure this light comes on before continuing.
If it does not, check your wiring from the previous section, most often this will be a wiring error.

For this section we will want to ensure the thermal camera is operational.
To do that we will need to start the docker container that houses all the code for the
thermal container as well as mqtt for so we can connect and send/receive messages
from the GUI

```bash
cd AVR-2022/VMC/
./start.py run mqtt thermal
```

navigate to the thermal view tab. You should see your thermal screen be populated.
Pass your hand in from of the camera to ensure it is seeing heat.
If it does not, feel free to try the auto-calibrate function or manually tune you calibration.
