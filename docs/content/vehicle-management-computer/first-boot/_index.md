---
title: "First Boot"
weight: 4
description: "After installing the operating system, set up the first user account"
---

{{% alert title="Warning" color="warning" %}}
Your Jetson should already have the operating system installed and configured for you.
These instructions are provided in case you need to wipe your Jetson and start fresh.
{{% /alert %}}

## Initial Setup

TODO flesh out more explictly with more picturess

{{% alert title="Note" color="note" %}}
If using a serial connection, all the navigation here on out will be done via your
keyboard. Use the arrow keys and <kbd>Tab</kbd> to move the cursor,
and <kbd>Enter</kbd> to confirm options.
{{% /alert %}}

![](jetson_hello.PNG)

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

{{< nextcopy >}}