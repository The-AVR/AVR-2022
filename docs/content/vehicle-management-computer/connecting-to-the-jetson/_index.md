---
title: "Connecting to the Jetson"
weight: 4
---

### Option 1 (KVM)

Possibly the simplest way to setup your Jetson with is a mouse, keyboard, monitor.
If you have ethernet available, plug that into the Jetson, as you will
need internet access. Otherwise, once you login to the Jetson,
connect to a WiFi network in the top right.

![Example for connecting to a WiFi network](image.png)

Once signed in, open up a terminal.
This can be done by clicking the application launcher
in the bottom left (the 9 squares) or with the shortcut
<kbd>Ctrl</kbd>+<kbd>Alt</kbd>+<kbd>t</kbd>.

### Option 2 (Serial)

The second (and more complicated) method of setting up your Jetson is using PuTTy
[like you did before]({{< relref "../../vehicle-management-computer/first-boot" >}}).
If you want to power the Jetson via USB (if it's not connected to
a wall adapter or a battery) remove the jumper behind the barrel jack,

![](image1.png)

then plug in the MicroUSB cable to the Jetson,

![](image2.png)

and then into your laptop. Open up PuTTy and log in to the Jetson.

If you have ethernet available, plug that in. Otherwise,
you can connect to WiFi via the command line (remove the
angle brackets when putting in your WiFi network details):

```bash
nmcli radio wifi on
sudo nmcli dev wifi connect '<wifi network name>' password '<wifi network password>'
```

Make sure to replace the jumper when you're done!

{{% alert title="Tip" color="tip" %}}
This method can also be helpful if you've already configured the
Jetson to connect to a WiFi network, but don't know what the IP address is.
{{% /alert %}}

### SSH

In the future, you'll want to use SSH to login to your Jetson,
as it is far easier. However, to do so, you'll need to know
the IP address of your Jetson. The simplest way to figure this out if
you don't know is to login via serial, and then run the command

```bash
ifconfig eth0
```

if you've connected the Jetson to ethernet or

```bash
ifconfig wlan0
```

if you've connected the Jetson to WiFi.

![](image3.png)

Once you've recorded this, you can then sign in with PuTTy.
Make sure to enter the hostname as `user@ip`.

![](image4.png)

You'll need to accept that you trust a certificate the first time.
