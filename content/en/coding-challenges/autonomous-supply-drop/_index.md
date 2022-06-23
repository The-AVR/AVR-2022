---
title: "Autonomous Supply Drop"
weight: 4
---

The purpose of this page is to help understand what it means to autonomously
perform the identification of the open path.

As always, the **official** rules for the game can be found
in the game manual located on the REC Foundation's website
[here](https://www.roboticseducation.org/teams/bell-vertical-robotics-competition/).

## What is meant by "autonomous"?

For the supply drop challenge, teams have the option of manually
dropping packages by using the ground control software on the laptop,
or by autonomously dropping the packages when the drone is in a suitable
condition to do so.

{{% alert title="Note" color="note" %}}
For the context of this challenge, autonomous means that the drone runs
software written by the team to release the package (control the actuator)
based on operating conditions without input from humans during the match.
As you are staging for your match, you will be given a manifest that details
which package must be dropped on which buildings, and will be allowed to
configure your program to operate accordingly.
{{% /alert %}}

If you take a look at the README for the repo over on
[GitHub](https://github.com/bellflight/VRC-2022/tree/main/VMC/FlightSoftware/README.md)
you'll see a list of all the topics and formats that are published over the MQTT broker.
For this challenge, you will want to find the topics for apriltags published by the
[apriltag module](https://github.com/bellflight/VRC-2022/tree/main/VMC/FlightSoftware/apriltag)
and and the topics used to control the actuators attached to the PCC.

Your program should take into account things like:

- **the drone's speed, which can be found on the "avr/velocity" topic**
  (is the drone moving fast or slow?)
- **the drone's position relative to the bullseye, which can be found on the "avr/apriltags/visible_tags" topic**
  (how close is the drone to the apriltag?)
- **the ID of the tag under the drone, also on the "avr/apriltags/visible_tags" topic**
  (which package should I drop?)
- **each actuator's relative position to the flight controller on the drone**
  (the positions reported by the apriltag module are relative to the flight controller.
  If your actuators are offset from the flight controller, your code should take that
  into account)

in order to decide when to publish a message to the "avr/pcc/set_servo_open_close"
topic and release a package.
