---
title: "Flashing the SD Card"
weight: 2
---

{{% alert title="Note" color="info" %}}
The steps that follow require that you've completed the setup of your computer
[here]({{< relref "../../../secondary-goal/laptop-setup" >}}).
{{% /alert %}}

Start by downloading the operating system for the Jetson from Nvidia's website
[here](https://developer.nvidia.com/embedded/downloads).
At the time of writing it is a 6 gigabyte file so it may take a while.

- Once that's downloaded, open Balena Etcher.
- Click "Flash from file" and select the file we just downloaded
- Make sure your SD card is inserted

{{% alert title="Note" color="info" %}}
If you're flashing an SD card that's been used before
(or if, let's say, you're starting over) make sure to format the SD Card
using the SD Card formatter we downloaded earlier.
{{% /alert %}}

- Click "Flash!"
- Wait for the SD Card to be flashed

{{% alert title="Success" color="success" %}}
Now you're ready for first boot!
{{% /alert %}}
