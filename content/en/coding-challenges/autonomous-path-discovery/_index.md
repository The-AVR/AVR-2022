---
title: "Autonomous Path Discovery"
weight: 3
---

The purpose of this page is to help understand what it means to autonomously
perform the identification of the open path.

As always, the **official** rules for the game can be found
in the game manual located on the REC Foundation's website
[here](https://www.roboticseducation.org/teams/bell-vertical-robotics-competition/).

## What is meant by "autonomous"?

For the search and rescue challenge, teams have the option of identifying the
path by either using the mounted projection or FPV camera to allow a ground
operator to **manually** observe which path is open and press a button to activate
the LED halo with the color of the open path, or to do the challenge **autonomously**.

{{% alert title="Note" color="note" %}}
For the context of this challenge, autonomous means that the drone
runs software written by the team to set the desired color of the
LED halo based on which tags are visible to the drone without input
from humans during the match.
{{% /alert %}}

If you take a look at the README for the repo over on
[GitHub](https://github.com/bellflight/AVR-2022/tree/main/VMC/FlightSoftware/README.md)
you'll see a list of all the topics and formats that are published over the MQTT broker.
For this challenge, you will want to find the topics for apriltags published by the
[apriltag module](https://github.com/bellflight/AVR-2022/tree/main/VMC/FlightSoftware/apriltag)
and the topics used to control the LED halo attached
to the PCC.

Your code should subscribe to certain topics on MQTT and publish commands
to the PCC with the "set_base_color" topic to set the color of red,
green, or blue depending on which apriltag ID is visible.
