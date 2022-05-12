# AprilTag Module

## What does this module do?

The apriltag module is responsible for using the images pulled from the CSI camera to scan for visible [apriltags](https://april.eecs.umich.edu/software/apriltag).

A low-level C++ program captures the images and hands them off to the Jetson's GPU for processing and publishes the raw detections to the "vrc/apriltags/raw" topic.

From here, a second program, written in python subscribes to this topic, and upon new detections, uses linear algebra to perform a coordinate transformation in order to get several pieces of data. These detections include the tags ID, as well as the drone's absolute location in the court (pos_world), and the drones relative location to the tag itself (pos_rel).

This data is then broadcast out over MQTT for other modules, such as the fusion and sandbox modules to consume.

## Windows Development

If you have trouble installing the `pupil-apriltags` package on Windows,
try installing
[https://aka.ms/vs/15/release/vs_buildtools.exe](https://aka.ms/vs/15/release/vs_buildtools.exe)
or the `visualstudio2017buildtools` Chocolately package.
You may need to add the VS 2017 Desktop Development C++ tools.
