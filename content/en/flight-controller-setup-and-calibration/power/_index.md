---
title: "Power"
weight: 6
---

## Power Setup

For correct display of battery percentage, you should always specify the
correct number of cells in the battery. In our case this will be 4 since we
are using a 4 cell LiPo battery. You should also calculate the value for
the voltage divider to calibrate the voltage readings coming from the power
module. This can be done by measuring the overall voltage with the Venom cell checker.
Then you can input the measured voltage into the `Calculate Voltage Divider` prompt.

These settings will provide you with an accurate battery percentage while the drone
is idle on the ground, so you can determine whether it is still safe to take off
and when you need to land. PX4 also has a fail-safe that prevents arming when the
battery percentage is too low. The video below walks through the power setup.

{{< youtube e8VeyTxQOcw >}}

{{% alert title="Note" color="note" %}}
If you would like to 3D print a few of the XT60 battery plug covers you can find them at the following link:
<a href="https://www.thingiverse.com/thing:341517" target="_blank">https://www.thingiverse.com/thing:341517</a>
{{% /alert %}}

## ESC Calibration

To ensure that all motors correctly respond to commands coming from the FC,
you should perform an ESC "calibration". It makes sure that the ESCs are aware of
the minimum and maximum pulse-width modulation (PWM) values that the FC provides.
This can be done by pressing the ESC calibration button and following
the on-screen prompts. The calibration process requires a USB connection since it
involves steps where you have to disconnect and reconnect the battery.
The video below covers this in detail.

{{< youtube 35fqT79MaAA >}}
