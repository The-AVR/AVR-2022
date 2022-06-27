---
title: "Glossary"
weight: 1
---

## 4S LiPo

4S LiPo refers to a Lithium Polymer battery that has 4 cells wired in series,
which means it has a fully charged capacity of 16.8V.
More info [here](https://rogershobbycenter.com/lipoguide).

## CW/CCW (Clockwise/Counterclockwise)

CW stands for Clockwise and CCW stands for Counterclockwise.
This refers to the direction a motor or propeller is meant to spin.
A CCW propeller on a CW motor will produce lift in the wrong direction,
so make sure to always double-check!

## Electronic Speed Controller (ESC)

An Electronic Speed Controller controls how fast a motor spins.
It receives a desired speed set-point from the Flight Controller and
adjusts the power going to the motor to match the requested speed.
More info on how they work [here](https://howtomechatronics.com/how-it-works/how-brushless-motor-and-esc-work/).

## Flight Controller (FC) or Flight Control Computer (FCC) or Flight Management Unit (FMU)

The Flight Controller can go by many names, but in practical terms, it just a
small computer that has sensors for determining the position and orientation of
the drone, along with circuitry for controlling motors based on input from a pilot
or autopilot. The flight controller used for the AVR
([NXP RDDRONE-FMUK66](https://www.nxp.com/design/designs/px4-robotic-drone-flight-management-unit-fmu-rddrone-fmuk66:RDDRONE-FMUK66))
is running the PX4 flight stack, which provides basic functionality you'd expect
from a hobby drone, and even some autonomy functions.

## Ground Control Station (GCS)

A ground control station is an operator station from which your drone
is controlled from. In our case, this will be a laptop running QGroundControl.
More info [here](https://en.wikipedia.org/wiki/UAV_ground_control_station).

## M3 Screw

An M3 screw is a metric screw with a 3mm diameter.
This type of screw is used to build the entire X4 500 frame.
More info [here](https://www.fastenermart.com/understanding-metric-fasteners.html).

## MAVLink (Micro Air Vehicle Link)

MAVLink is a standard protocol to send messages between a ground control station
and an unmanned vehicle and vice versa. These messages include important information
such as velocity, attitude, battery state, waypoints, etc.
More info [here](https://en.wikipedia.org/wiki/MAVLink).

## MAVLink Router/MAVP2P

MAVLink Router and MAVP2P are both pieces of software that help to connect multiple
MAVLink devices together. A standard MAVLink setup has a ground control station
communicating directly with an unmanned vehicle, but these pieces of software allow
you to connect a single ground control station to multiple vehicles or vice versa.
More info [here](https://github.com/mavlink-router/mavlink-router) for MAVLink Router
or [here](https://github.com/aler9/mavp2p) for MAVP2P.

## Peripheral Control Computer (PCC)

The Peripheral Control Computer is a microcontroller running custom software that
accepts requests from things like your laptop or, later on, the VMC to control
servos and LEDs that are attached to it.

## Power Distribution Board (PDB)

A Power Distribution Board is connected to your battery and takes the power coming
from the battery and distributes it to the various components on your drone at the
voltages and currents that they expect.
More info [here](https://dronenodes.com/pdb-power-distribution-board/).

## PX4

PX4 is an open-source autopilot software stack. This contains low-level algorithms
running on the flight controller that constantly interpret things like position,
attitude, altitude, heading, etc. and adjust the motors to keep your drone on
course and can manipulate the drone to fly to desired positions.
More info on PX4 [here](https://px4.io/).

## QGroundControl (QGC)

QGroundControl is ground-control software for drones and other unmanned vehicles.
It allows you to easily connect to a drone and give it commands such as to takeoff,
land, and uploading missions to it for it to perform.
More info [here](http://qgroundcontrol.com/).

## R/C Controller

An R/C (radio-controlled) Controller can be used with QGroundControl to manually
fly your drone while not in autonomous mode.
More info [here](https://docs.qgroundcontrol.com/master/en/SetupView/Radio.html).

## Vehicle Management Computer (VMC)

The Vehicle Management Computer is the companion computer that performs various
tasks and communicates with the Flight Controller. This is where your custom software
will be run to complete the challenges for the competiton.

## Advanced Vertical Robotics (AVR)

The Advanced Vertical Robotics competition is a robotics competition put on by Bell Flight
to challenge high school students to develop STEM skills outside of the classroom
and work together to solve engineering challenges in a fun robotics competition
in the vertical dimension.

## X4 500

The X4 500 is the frame of your drone. This is what all of the components will
be mounted to.
More info [here](https://www.amazon.com/dp/B087LT81C8/).
