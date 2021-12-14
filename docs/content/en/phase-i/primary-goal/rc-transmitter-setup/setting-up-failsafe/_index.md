---
title: "Setting Up Failsafe"
weight: 5
---

By default, when the RC receiver loses connection with the transmitter,
the receiver will continue sending the latest known stick position to the FC.
While this can be useful in some situations, it is very dangerous for flying drones:
**it can result in fly-away situations whenever signal is lost!** To change this, the
failsafe option in the function tab of the settings menu can be used. It allows us
to set a desired value for each channel to take on whenever the transmitter loses connection.

{{% alert title="Warning" color="warning" %}}
Setting up proper fail-safes is **very important** for your own safety and the
safety of your environment! Don't neglect this, and review your setup regularly!
{{% /alert %}}

While the FC should be able to detect signal loss and has different options to
react in such a situation, we also recommend a good failsafe setup on
the RC transmitter, as a last resort in case the FC does not detect the signal loss.

We recommend setting the failsafe options as follows in terms of stick and
switch positions. This will cause the drone to shut down its motors when
the FC does not detect the signal loss. This is the only viable option,
**it is not safe to keep the drone in the air when we do not have any control over it.**

We will later have a look at failsafe options in the FC configuration as well.
For now, we will set the RC transmitter failsafe to:

- Left stick (throttle/yaw) to the bottom and horizontally centered.
- Right stick (pitch/roll) both horizontally and vertically centered.
- Switches **SWA**, **SWB**, and **SWC** in the upward position, **SWD** in the downward position.

This will set the throttle to zero and reset the yaw, roll,
and pitch to neutral angles. We will later assign functions to the switches,
where the upper position will be the default state. We will assign a kill switch
function to **SWD**. With this failsafe setting, the receiver will emulate
the kill switch being flipped when it loses connection, and ultimately
disable the motors.

![Default stick/switch positions with SWD kill switch enabled (toggled down)](failsafe_positions.jpg)

{{% alert title="Note" color="note" %}}
Channel values are normally represented by a range of -100% to 100%.
For example, the throttle stick (left stick vertical axis) is assigned to CH3.
When the throttle stick is all the way down CH3 is set to -100% and when it
is all the way up (maximum throttle) CH3 is set to +100%.
{{% /alert %}}

To begin setting up failsafe values, go to the **Failsafe** screen from
the **Function** screen in the **Settings** menu.

![Default failsafe screen](failsafe_default.jpg)

To set up a failsafe for a channel, tap the <kbd>Off</kbd> button next to the channel.
In the screen that appears, tap the <kbd>On</kbd> button to enable the failsafe
for that channel.

![Setting up failsafe for CH1](failsafe_channel_enabled.jpg)

Now make sure the stick/switch belonging to that channel is in the correct position.
In the case of **CH1**, which is assigned to the right stick, it will be horizontally
and vertically centered. Now tap the <kbd>Setup</kbd> button to save this position.

![CH1 failsafe value set to 0%](failsafe_setup.jpg)

After tapping <kbd>Setup</kbd> you will be taken to the main failsafe screen
where you can configure the failsafe for the rest of the channels.

![CH1 failsafe value set to 0% (right stick centered)](failsafe_ch1.jpg)

Go ahead and complete the failsafe configuration for Channels 2, 3, and 4.
When finished you should see something identical to the image below.

![Failsafe configuration for Channels 1-4](failsafe_ch1_through_ch4.jpg)

We will now set up failsafe values for the switches we configured in
the previous section. Let's run through an example of doing this for **CH5**,
which is attached to **SWA**. Make sure **SWA**, **SWB**, and **SWC** are in
the up position and **SWD** is in the down position.

![Setting up failsafe for CH5 attached to SWA](failsafe_ch5.jpg)

Tap <kbd>On</kbd> and then <kbd>Setup</kbd> for **CH5**. This will set a value of -100%
for **CH5** (**SWA** up position) as shown below.

![CH5/SWA default switch position up with a value of -100%](failsafe_ch5_up.jpg)

Tap the back arrow and complete the process for Channels 6-8.
Keep in mind that since **CH8** (switch **SWD**) is in a downward position the value
will be +100% as shown in the photo below.

![CH8/SWD down switch position with a value of +100%](failsafe_ch8.jpg)

The following photo shows the final failsafe values for Channels 5-8.
These are the values that will be sent from the receiver to the FC in
case there is a loss of signal with the transmitter.

![Failsafe configuration for channels 5-8](failsafe_aux_channel_values.jpg)

The failsafe values for all channels have been configured. In the end,
you should have the following failsafe values for each of the channels:

| Channel      | Fail-safe value | Stick/Switch Position        |
| ------------ | --------------- | ---------------------------- |
| 1 (Roll)     | 0%              | Right stick centered         |
| 2 (Pitch)    | 0%              | Right stick centered         |
| 3 (Throttle) | -100%           | Left stick down and centered |
| 4 (Yaw)      | 0%              | Left stick down and centered |
| 5            | -100%           | SWA up                       |
| 6            | -100%           | SWB up                       |
| 7            | -100%           | SWC up                       |
| 8            | 100%            | SWD down                     |

Your transmitter setup is now complete and we will move on to
setting up and calibrating the FC.

{{% alert title="Warning" color="warning" %}}
Setting up proper fail-safes is **very important** for your own safety and the
safety of your environment! Please take the time to carefully review this page
one more time.
{{% /alert %}}
