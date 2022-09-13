---
title: "Connecting to the Jetson"
weight: 1
---

You'll need to login to your Jetson many times to setup and run software.
Out of the box, your Jetson will have a default user account called
`avr` with a password of `bellavr22`.

Here are 3 possible methods you can use.

## Monitor and Keyboard

---

Possibly the simplest way to connect to your Jetson is with
a monitor and keyboard. You'll just need a monitor that has HDMI or DisplayPort
that you can plug in to the Jetson.

Once at the desktop,
you can open a terminal by clicking the application launcher
in the bottom left (the 9 squares) or with the keyboard shortcut
<kbd>Ctrl</kbd>+<kbd>Alt</kbd>+<kbd>t</kbd>.

## Serial

---

If you do not have a monitor and keyboard, another method of logging in to your Jetson is over a serial connection.
To do this, you'll need a serial client.

### Installing Serial Client

---

#### Installing Serial Client on Windows

For Windows, we recommend PuTTy.
Go to [this page](https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html)
and download and install the `putty-64bit-<version>-installer.msi` file.

![Download this installer file](2022-05-20-09-53-32.png)

![Run through the setup wizard](2022-05-20-09-54-21.png)

#### Installing Serial Client on MacOS

Rather than using PuTTy, it's much easier to open a terminal and simply run:

```bash
screen ttyACM0 115200
```

#### Installing Serial Client on Linux

You can follow the same steps as on MacOS
(after installing `screen` with `sudo apt install screen`),
but if you like a GUI, you can
install PuTTy with:

```bash
sudo apt install putty
```

and launch PuTTy with:

```bash
sudo putty
```

### Connecting to Jetson via Serial Client

---

Now, if you want to power the Jetson via USB (if the Jetson is not connected to
a wall adapter or a battery) remove the jumper behind the barrel jack.

![](image1.png)

{{% alert title="Tip" color="tip" %}}
Keep this somewhere safe, like sticking it to a piece of tape, it's very easy to lose!
{{% /alert %}}

Plug in a MicroUSB cable to the Jetson,

![](image2.png)

and then into your computer.

{{% alert title="Tip" color="tip" %}}
For Windows, open up Device Manager,

![](2022-06-15-19-42-25.png)

and find out what COM port your Jetson is on.

![Look under Ports (COM & LPT). My Jetson enumerated as COM4](comport.PNG)
{{% /alert %}}

Open up PuTTy, choose the COM port or the serial device `/dev/ttyACM0` for the
Serial line, and put in `115200` as speed.

![](putty_config.PNG)

Click "Open". You should now see the Jetson's terminal.

{{% alert title="Tip" color="tip" %}}
This method can also be helpful if you've already configured the
Jetson to connect to a network, but don't know what the IP address is.
{{% /alert %}}

## SSH

---

{{% alert title="Note" color="note" %}}
This only works if you've already configured the operating system on the Jetson.
If you're setting up your Jetson from scratch, you'll first need to start by
using Monitor/Keyboard or Serial.
{{% /alert %}}

In the future, you'll want to use SSH to login to your Jetson,
as it is far more convenient. SSH is way to login to a Linux system
over a network. However, to do so, you'll need to know
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

![](ifconfig-wlan0.png)

If you have yet to connect your jetson to the WiFi you can follow instructions for
[connecting to internet]({{<relref "../updating-vmc-software/#connecting-to-internet">}})
prior to returning to connect through ssh.

### `ssh` Command

The quickest way to login to yor Jetson over SSH, is to use the builtin `ssh` command
in Windows. Open up a command prompt or PowerShell, and run

```powershell
ssh <user>@<ip>
```

The first time you log in to your Jetson, you'll be prompted to accept
the host's key. Enter `yes`. You'll thenbe prompted for your password,
and then you'll be put into a terminal.

![Command line SSH login](ssh-avr.png)

### PuTTy

If you're not comfortable with the command line, you can install PuTTy to connect
over SSH. Select the "SSH" button in PuTTy, put in the hostname field `<user>@<ip>`
and then click the "Open" button.

![PuTTy SSH Login](putty-ssh-avr.png)

![Secondary popup window](putty-ssh-success-avr.png)

You'll need to accept that you trust a key the first time.

![Accept the key](2022-06-15-19-54-20.png)

### SSH Troubleshooting

#### Connection closed/reset

If you try to SSH into your Jetson, and you immediately get a connection
timed out error, here's how to fix it.

First, login to your Jetson via serial. Run the command

```bash
tail /var/log/auth.log
```

and see that you're getting errors about invalid formats:

```text
Jun 28 18:42:26 drone sshd[8547]: error: key_load_private: invalid format
Jun 28 18:42:26 drone sshd[8547]: error: key_load_public: invalid format
Jun 28 18:42:26 drone sshd[8547]: error: Could not load host key: /etc/ssh/ssh_host_ecdsa_key
Jun 28 18:42:26 drone sshd[8547]: error: key_load_private: invalid format
Jun 28 18:42:26 drone sshd[8547]: error: key_load_public: invalid format
Jun 28 18:42:26 drone sshd[8547]: error: Could not load host key: /etc/ssh/ssh_host_ed25519_key
Jun 28 18:42:26 drone sshd[8547]: fatal: No supported key exchange algorithms [preauth]
```

If so, run the command

```bash
sudo /usr/bin/ssh-keygen -A
```

to generate a new host key.

{{% alert title="Note" color="note" %}}
You may need to delete or edit your ~/.ssh/known_hosts file after you do this.

![Host key verification failed](2022-06-28-18-49-22.png)

{{% /alert %}}
