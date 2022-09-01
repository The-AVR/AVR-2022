---
title: "System Setup"
weight: 2
---

{{% pageinfo color="warning" %}}
Your Jetson should already have the operating system installed and configured for you.
These instructions are provided in case you need to wipe your Jetson and start fresh.
{{% /pageinfo %}}

## Initial Setup

{{% alert title="Note" color="note" %}}
If using a serial connection, all the navigation here on out will be done via your
keyboard. Use the arrow keys and <kbd>Tab</kbd> to move the cursor,
and <kbd>Enter</kbd> to confirm options.
{{% /alert %}}

![](2022-06-18-16-13-30.png)

Select "Ok"

![](2022-06-18-16-14-17.png)

Scroll through agreement and select "Ok"

![](2022-06-18-16-14-42.png)

Select your language

![](2022-06-18-16-15-05.png)

Select your country

![](2022-06-18-16-15-25.png)

Select your timezone

![](2022-06-18-16-15-40.png)

Allow clock to be set to UTC

## Creating your account

![](2022-06-18-16-16-17.png)

Enter a name, such as your school's name

![](2022-06-18-16-16-42.png)

Choose a username, such as "avr"

![](2022-06-18-16-17-00.png)

Choose a password

![](2022-06-18-16-17-37.png)

Retype your chosen password

![](2022-06-18-16-18-12.png)

When asked about resizing the partition, leave the default.

## Network Configuration

![](2022-06-18-16-21-18.png)

Setting up a network connection is not needed at this time. To bypass this, select
"dummy0" and let the autoconfiguration fail.

![](2022-06-18-16-22-14.png)

![](2022-06-18-16-22-28.png)

Go ahead and select "Do not configure the network at this time".

## Final Setup

![](2022-06-18-16-23-21.png)

Select an appropriate [hostname](https://xkcd.com/910/) for your Jetson.
"drone" is a good choice.

![](2022-06-18-16-24-35.png)

Choose the "MAXN" power mode.

![](2022-06-18-16-24-52.png)

Let the installation finish. Once it's done, reboot your Jetson.
