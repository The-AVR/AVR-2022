---
title: "Setting the Output Mode"
weight: 3
---

In the world of drones and radio controllers, there are a lot of different protocols
in use. More information about these different protocols can be found
[here](https://oscarliang.com/pwm-ppm-sbus-dsm2-dsmx-sumd-difference/).
The FlySky FS-iA6B receiver that was included with the FlySky FS-i6S transmitter
supports PWM, PPM, S.BUS, and i-BUS output, but the FC in the AVR kit only supports
PPM and S.BUS. For the AVR drone, it is recommended to use the S.BUS protocol since
it is the most stable of the two and supports more channels.

Configuring the RC receiver to output the S.BUS protocol can be done in the
**OUTPUT MODE** screen shown below. You can find the
**OUTPUT MODE** screen on the **system** view in the **settings** menu.
Everything should be configured as shown in the picture.
This will set PPM and S.BUS as the output communication protocols, which will be
available on separate pins. The FC has already been connected to the pins on
which S.BUS output will be available.

![Output mode configured for PPM and S.BUS](ppm_settings.jpg)

Changes are automatically saved so you can tap on the back arrow to go to the
previous menu. If you power down your transmitter these settings will
still be maintained.
