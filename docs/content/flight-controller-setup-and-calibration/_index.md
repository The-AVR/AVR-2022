---
title: "Flight Controller Setup and Calibration w/ QGC"
weight: 5
description: "In this section we'll walk through the final steps of loading firmware and calibrating your drone before your first flight."
---

## QGroundControl (QGC)

Ground control software is used for configuration and monitoring of your VRC drone.
We will be using QGroundControl as our ground control software of choice
throughout VRC. With QGC you can upload firmware, configure flight modes,
calibrate sensors and much more. It also provides different ways of controlling
the drone, such as an autonomous mission planner.

QGC can be downloaded and installed on Windows, Mac, and Linux operating systems.
You can find the necessary installer by going to the
[downloads page](http://qgroundcontrol.com/downloads/).
Go ahead and install QGC before proceeding to the next section.

{{% alert title="Note" color="note" %}}
All testing and configuration throughout the documentation was done
with QGC version 4.1.1. We encourage you to use this version,
which will allow us to help troubleshoot any issues more easily.
You can find the file labeled `QGroundControl-Installer.exe` at
[this link](https://github.com/mavlink/qgroundcontrol/releases/tag/v4.1.1).
{{% /alert %}}

The following sections will guide you through the process of using
QGC to set up your FC. Let's get started!
