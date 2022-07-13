---
title: "First Boot"
weight: 3
description: "After installing the operating system, set up the first user account"
---

{{% alert title="Warning" color="warning" %}}
Your Jetson should already have the operating system installed and configured for you.
These instructions are provided in case you need to wipe your Jetson and start fresh.
{{% /alert %}}

## Installing PuTTy

To easily connect to your Jetson, you need to download and install a tool called PuTTy first.
Go to [this page](https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html)
and download and install the `putty-64bit-<version>-installer.msi` file.

![Download this inntaller file](2022-05-20-09-53-32.png)

![Run through the setup wizard](2022-05-20-09-54-21.png)

## Connecting to your Jetson

- Make sure to remove the jumper that says "ADD JUMPER TO DISABLE USB POWER"
  that's just behind the barrel jack
- Insert your SD card under the heatsink
- Plug your jetson into the PC
- Start PuTTy
- Go to device manager, and find out what port your Jetson is on

![Look under Ports ( COM & LPT ). My Jetson enumerated as COM4](comport.PNG)

- Back in PuTTY, choose serial.
- Choose the COM port you found above for the Serial line, and 115200 as speed.

![](putty_config.PNG)

- Click "Open"
- You should now see the Jetson's terminal

![](jetson_hello.PNG)

{{% alert title="Note" color="note" %}}
All the navigation here on out will be done via your keyboard when using PuTTY.
Use the arrow keys and <kbd>Tab</kbd> to move the cursor, and <kbd>Enter</kbd> to
confirm options.
{{% /alert %}}

- Hit <kbd>Enter</kbd>
- Scroll through agreement and hit <kbd>Enter</kbd>

## Setting your Locale

- Choose English for your language
- Choose US for your country
- Select your timezone
- Allow clock to be set to UTC

## Creating your account

- Enter a name, such as your school's name
- Choose a username, I chose "vrc"
- Choose a password
- When asked about resizing the partition, hit <kbd>Enter</kbd>

## Setting the Power Mode

Choose the "maxn" power mode

