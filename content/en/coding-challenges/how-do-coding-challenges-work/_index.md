---
title: "How Do Coding Challenges Work?"
weight: 1
---

During the competition teams will be encouraged to participate in two coding challenges.

Challenge 1 will be to leverage the
[AprilTags](https://roboticsknowledgebase.com/wiki/sensing/apriltags/) that will be
placed throughout the competition court in order to identify
which of the three rescue paths are open for the Rover to rescue
the stranded hikers.
Check out more about this challenge at the link below:

{{< card header="" >}}
[Autonomous Path Discovery]({{< relref "../autonomous-path-discovery" >}})
{{< /card >}}

Challenge 2 will be to leverage the AprilTags and other data from onboard sensors to
autonomously drop supplies to various buildings on the court.
Check out more about this challenge at the link below:

{{< card header="" >}}
[Autonomous Supply Drop]({{< relref "../autonomous-supply-drop" >}})
{{< /card >}}

## How do we perform the coding challenges?

In the
[GitHub repository](https://github.com/bellflight/AVR-2022/tree/main/VMC/README.md)
we've provided an area for you to write
Python in order to accomplish your goals. The software stack for AVR is
made up of a series of modules, which are actually independent
[Docker Containers](https://www.docker.com/resources/what-container).

Below is a graphic that shows the individual containers:

![](phaseI-Page-2.drawio.png)

All of these modules communicate with each other over a message bus called
[MQTT](http://www.steves-internet-guide.com/mqtt-works/).
You could loosely think of MQTT like a social media feed.
You can **publish** posts and your friends can **subscribe** to your feed to see them.
Similarly, you can subscribe to your friends' feeds and see their posts too.

Below is a non-exhaustive list of the kinds of data some of the modules publish:

- Flight Control Module
  - Drone Position
  - Drone Orientation
  - Drone Velocity
  - Drone Flight Mode
  - Drone Battery Level
- AprilTag Module
  - Visible AprilTag IDs
  - Their relative Positions
- VIO Module
  - T265 Position
  - T265 Velocity
  - T265 Confidence
- PCC Module
  - Actuator States (Coming Soon)
  - LED Halo States (Coming Soon)
- Fusion Module
  - Coordinate Transformed Drone Position

Your job for the coding challenge will be to subscribe to the
necessary topics above and write your own logic to produce the
desired output (setting of the LED Halo and actuator positions)
based on given input.
