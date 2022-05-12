---
title: "Flash the PCC"
weight: 3
---

To flash your PCC, you need to download and install a tool called BOSSA first.
Go to [this page](https://github.com/shumatech/BOSSA/releases/) and download and install
the `bossa-x64-<version>.msi` file. Make sure to install the device drivers
that it prompts you to install as well.

![Download this installer file](2022-05-12-07-12-10.png)

![Run through the setup wizard](2022-05-12-07-12-59.png)

After getting BOSSA installed, you need to also download the PCC firmware that you'll
be loading. Go to the
[VRC release page](https://github.com/bellflight/VRC-2022/releases/tag/stable)
and download the `pcc_firmware.<version>.bin` file.

![Download this firmware file](2022-05-12-07-14-49.png)

Now you're ready to flash your PCC! Follow the next steps _exactly_ to not
run into any issues.

First, plug your PCC into your computer with the provided MicroUSB cable.
Open Device Manager in Windows, and you should see at least one entry under
"Ports (COM & LPT)" (if this doesn't happen, that's okay, it means the firmware isn't
loaded or corrupted, but we're about to overwrite it anyways).

![Normal PCC COM port](2022-05-12-07-20-39.png)

Quickly double-tap the little reset button right next to the MicroUSB connector.
The LED next to the button should briefly flash red before turning solid green.
Additionally, the PCC should also now show up as a USB device in Windows
titled "FEATHERBOOT", and the COM port you saw before should now be gone and
replaced with one with a different number. This puts the PCC into bootloader mode
so we can flash new firmware.

![Bootloader PCC COM port](2022-05-12-07-21-43.png)

Open BOSSA and select the COM port that has now shown up from the previous step.
Also select the firmware file you downloaded.

{{% alert title="Warning" color="warning" %}}
Forgetting this next step will cause lots of confusing results!
{{% /alert %}}

In BOSSA, **make sure to put in a flash offset of `0x4000`** and select "Erase all".

![BOSSA settings](2022-05-12-07-32-22.png)

Now, you can hit the "Write" button!

![Flashing complete](2022-05-12-07-34-07.png)

You can also optionally click the "Verify" button as well just to make sure
everything flashed correctly.

![Verificiation complete](2022-05-12-07-36-32.png)

Finally, to get the PCC out of bootloader mode, and make sure the firmware is working
correctly, unplug the PCC and plug it back in, or press the reset button once.
The bright green LED should remain off and the original COM port should show
back up in device manager.

{{% alert title="Success" color="success" %}}
You're now ready to test it out!
{{% /alert %}}
