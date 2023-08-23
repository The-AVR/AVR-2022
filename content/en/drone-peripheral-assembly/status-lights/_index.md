---
title: "LED Status Lights"
weight: 5
---

The status lights are designed to provide an extra layer of quick and easy debugging to show the status of your drone at a glance.

To complete the status light installation you will need the following.

![Components with wires cut to 3"](led_status_1.jpg)

## Wiring

Wire the green wire to DIN, red wire to 5VDC, and black wire to Ground. Remove the plastic housing from other end of the wires.

![LED soldered and ready for VMC wiring](led_status_2.jpg)

Insert wires into VMC housing per the following wiring diagram.

![Jetson Header Wiring Diagram](jetson_pinout.jpg)

This should result in the following.

![LED connected to VMC housing](led_status_3.jpg)

## Mounting

Use 3M double-sided foam tape to mount to the fan of the Jetson facing towards the rear of the drone.

![Adhesive for mounting LED](led_status_4.jpg)

![LED mounted on rear side of cooling fan](led_status_5.jpg)

## Testing

{{< youtube 7TZ5N8Uggcs >}}

Commands run in video:

```bash
cd AVR-2022/VMC/
./start.py run -n
```

Feel free to explore and try different combinations for what you think is the most useful information.
For instance if you are doing just a flight test with no peripherals you may want to try the following.

```bash
cd AVR-2022/VMC/
./start.py run status -m
```

## Light Definition

| Module:   | Message:        | LED: | Color: |
| --------- | --------------- | ---- | ------ |
| VIO:      | "avr/vio"       | 1    | PURPLE |
| PCM:      | "avr/pcm"       | 2    | AQUA   |
| Thermal:  | "avr/thermal"   | 3    | BLUE   |
| FCC:      | "avr/fcm"       | 4    | ORANGE |
| AprilTag: | "avr/apriltags" | 5    | YELLOW |
