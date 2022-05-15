---
title: "Test the PCC"
weight: 4
---

## Physical Setup

On your PCC, we'll need to make use of a USB power jumper to
power the servos from our laptop.

![Installed USB power jumper](DSC02217.jpg)

{{% alert title="Warning" color="warning" %}}
MAKE SURE to **ONLY** use the jumper when testing with your laptop.
**NEVER** use the USB power jumper when the PCC is connected to the Jetson.
This is because the servos may draw enough current in certain scenarios
that would cause the current protection to trip on the power supply and
power off the Jetson regardless of what it's doing.
{{% /alert %}}

![](DSC02218.jpg)

Plug your servos and LED strip into the designated connections on the PCC:

- The LED strip plugs into the prop-maker featherwing
- The servos plug into channels 0-3, with the yellow signal wire of
  the servo facing the Adafruit logo on the PCB.

### Back at the Computer

TBD

{{% alert title="Success" color="success" %}}
Click around and try the different buttons,
your PCC should light up the LED and move some servos!
{{% /alert %}}
