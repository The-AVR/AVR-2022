---
title: "Charging"
weight: 2
---

## Charging the Battery

Please read the manual prior to beginning your first charge.
The manual comes with your charger or you can find a
[digital version here]({{< static "/files/VenomPro2ChargerManual.pdf" >}}).

![Venom Pro 2 Charger](image12.jpg)

Unbox the charger, you will be using the power cord,
as well as the "XT60" charge lead pictured below.

![XT60 charge lead](image.png)

Connect the power cable to the back of the unit, and plug it in.
Then connect the Charge lead to the charger, ensuring that the black wire
is plugged into the black terminal and the red wire is plugged into the red terminal.
This will ensure the correct polarity.

![Charger powered up](image7.jpg)

Press the SELECT button on the charger until you see the menu
labeled "Program Select-LiPo Batt".

![Program Select menu](image1.png)

Plug the battery into the charger, using the balance cable on the battery.
The balance cable is the small black connector with 4 black wires and 1 red wire.
This allows the charger to balance the cells of the battery.

{{% alert title="Warning" color="warning" %}}
The balance connector should always be used whenever the
battery is being used with the charger.
{{% /alert %}}

![Balance connector plugged in](image18.jpg)

Plug the battery main lead (the yellow XT60 connector) to the main lead on the charger.

![XT60 connector plugged in](image16.jpg)

Now that the battery is connected to the charger,
turn your attention back to programming the charger. Press Enter.

![Program Select menu](image13.jpg)

Press the INC button until the display reads, "LiPo Balance" then press Enter.
You will want to use this setting for each charge.

The amps setting will begin to flash, adjust the amperage to "5.0A" using the
INC/DEC buttons as necessary, then press enter.

The voltage setting will begin to flash, adjust the voltage to
"14.8V (4S)" using the INC/DEC.

![LiPo Balance charge set to 5.0A](image15.jpg)

Once the setting on your charger matches the setting shown above,
press and hold the START/ENTER button until the display reads,
"Battery check wait…". You can release the START/ENTER button at that point.

![Battery check in progress](image21.jpg)

The charger will now ask you to confirm that the cell count it detects is
the same cell count that you entered.
R=Recognized (by the charger) S=Selected (by the user.)
Provided those values match, press ENTER to begin the charge process.

![Confirming cell count before charging](image17.jpg)

Once you have initiated the charge, you will see the charge status screen
pictured below.

![Balance charge in progress](image14.jpg)

- **Li4S** Indicates a 4S LiPO battery is charging.
- **15.47V** in this case indicates the overall pack voltage,
  your value will change throughout the charge. At completion, the voltage
  should read around 16.8V.
- **BAL** Indicates that you are performing a balance charge. Always balance charge.
- **000:16** Indicates the amount of time in minutes and seconds the
  battery has been charging.
- **00016** Indicates the approximate amount of mAh that have gone into the
  battery since the charge was initiated.

{{% alert title="Note" color="note" %}}
While the battery has a capacity of 5000mAh, you will likely not put 5000mAh
into the battery on charging. We can only put in what we have taken out.
A LiPO battery cannot be run down to 0.0V per cell, it cannot go lower
than 3.0V per cell without being damaged.
{{% /alert %}}

When your battery is finished charging you will see "Full" in the top left.
All other numbers will stop fluctuating and the final (fully charged) voltage of
the battery will be shown in the top right corner
(this should be **16.8V** or very close to it.)

