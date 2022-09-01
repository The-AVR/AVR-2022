---
title: "Flight Controller Setup and Calibration w/ QGC"
weight: 7
description: "In this section we'll walk through the final steps of loading firmware and calibrating your drone before your first flight."
---

## QGroundControl (QGC)

Ground control software is used for configuration and monitoring of your AVR drone.
We will be using QGroundControl as our ground control software of choice
throughout AVR. With QGC you can upload firmware, configure flight modes,
calibrate sensors and much more. It also provides different ways of controlling
the drone, such as an autonomous mission planner.

QGC can be downloaded and installed on Windows, Mac, and Linux operating systems.
You can find the necessary installer by going to the
[downloads page](https://docs.qgroundcontrol.com/master/en/releases/daily_builds.html).
Using the daily build, follow the steps
[here](https://docs.qgroundcontrol.com/master/en/getting_started/download_and_install.html)
for your operating system.

Go ahead and install QGC before proceeding to the next section.

{{% alert title="Note" color="note" %}}
For Ubuntu 22.04 users, you may need to additionally install `libfuse2` before the
AppImage will work:

```bash
sudo apt install libfuse2
```

{{% /alert %}}

The following sections will guide you through the process of using
QGC to set up your FC. Let's get started!
