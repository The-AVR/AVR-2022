---
title: "VMC and PCC Power"
weight: 1
---

Two main components of your advanced build are the **Vehicle Management Computer**
(VMC), which runs the AVR software stack and the **Peripheral Control Computer** (PCC),
which will allow teams to manually and programmatically control the LED ring
and actuate up to four servos.

This section will walk through the necessary steps for providing adequate
power to both the VMC and PCC. This will be done with two separate buck
converters, which are included in **Box 5** of your kit. The main battery of your
AVR drone is 16.8V fully charged. The required input voltage for the VMC and PCC
are 5V, therefore the buck converters will step the voltage down to a usable 5V.

## VMC Buck Converter

The following steps will be repeated for both buck converters and connected
to the PDB of the AVR drone. Start off by locating the heat shrink tubing and
male bullet connectors as seen below.

![Heat shrink tubing, bullet connectors, and buck converter](bullet_connectors1.jpg)

{{% alert title="Note" color="note" %}}
The heat shrink tubing will be longer than necessary. Cut two pieces of tubing
approximately 2" in length using scissors.
{{% /alert %}}

Place heat shrink tubing over the black and red leads of the buck converter.
Clamp one of the bullet connectors using the tool of your choice and fill
the cup with solder.

{{% alert title="Note" color="note" %}}
If you don't have a tool to hold the bullet connector one thing you
can do is drill a hole into a small piece of wood, such as an old
piece of 2x4, and place the bullet connector into the hole with the cup facing up.
{{% /alert %}}

![Filling the bullet connector with solder](bullet_connectors2.jpg)

Quickly remove the solder tip and place one of the black or red leads into the cup.
Keep it there for a few seconds until the solder hardens.

{{% alert title="Danger" color="danger" %}}
Bullet connectors conduct a lot of heat, so make sure not to touch the connector
for a minute or two after it's filled with solder.
{{% /alert %}}

![Positive and negative leads with bullet connectors soldered](bullet_connector3.jpg)

After the bullet connectors are soldered into place you will apply the heat shrink.
Pull the heat shrink down over the end of the bullet connector as shown
in the photo below and apply heat. If you have access to a heat gun or
a lighter this will work well. Alternatively, you can use the side of
your soldering iron to apply heat and let the tubing shrink over your connectors.

![Apply heat shrink with asoldering iron](heat_shrink_soldering_iron.jpg)

After applying heat shrink to the bullet connectors they should
look similar to the photo below.

![Bullet connectors and heat shrink applied to VMC buck converter](heat_shrink_complete.jpg)

With the input side (16.8V) of the buck converter complete we need to
take care of the output side. This is what we will plug into the VMC
using a DC barrel plug to provide a constant 5V.
The barrel plugs are located in **Box 5** of your AVR kit.

![Barrel plugs from the AVR kit](vmc_barrel_plug.jpg)

Out of the package the barrel plugs are longer than necessary.
Cut one to approximately 4-5" which is a good length that we'll
solder to the black and yellow leads of the buck converter.

![Barrel plug trimmed and ready for soldering to buck converter](cut_barrel_plug.jpg)

We will prep the black and yellow leads with heat shrink before soldering begins.
The photo below shows heat shrink over each of the individual leads and
a larger piece covering both leads. This will allow us to keep our
connections nice and tidy.

{{% alert title="Tip" color="tip" %}}
Be sure to slide the heat shrink onto the leads **BEFORE** soldering.
Otherwise you will not be able to do so after soldering is complete.
{{% /alert %}}

![Black and yellow output leads prepped with heat shrink and ready for soldering](buck_converter_heat_shrink_for_barrel_plug.jpg)

Soldering two leads together isn't always the easiest chore so be
sure to use the right tool to keep the leads steady and then solder them together.

{{% alert title="Note" color="note" %}}
It's incredibly important that you solder the
<span style="background-color: red;">**RED**</span> lead from the barrel plug to the
<span style="background-color: yellow;">**YELLOW**</span> lead of the buck converter.
Then the **BLACK** lead from the barrel plug to the **BLACK** lead of
the buck converter.
{{% /alert %}}

![Red and yellow wires soldered together](solder_buck_converter_output_leads.jpg)

After soldering the leads together you should have something that looks
like the photo below.

![Positive (red/yellow) and negative (black/black) wires soldered together](buck_converter_output_leads_soldered.jpg)

Given we want to prevent a short circuit between the positive and negative
connections we will apply heat shrink to the solder joints.

![Positive and negative joints with heat shrink applied](red_yellow_barrel_plug_and_buck_converter.jpg)

Slide the last piece of heat shrink down and apply heat to it.
This step is completely optional, but it does help keep your cable nice and tidy.

![Barrel plug connected to buck converter and ready to power VMC](buck_converter_complete.jpg)

Good job! Now let's quickly go over how to get the other buck converter
ready for the PCC.

## PCC Buck Converter

The PCC requires 5V of input power and will use the second buck converter in
your AVR kit. Follow the steps covered in the VMC power setup by soldering bullet
connectors to the red and black leads of the buck converter.

![Bullet connectors and heat shrink applied to PCC buck converter](heat_shrink_complete.jpg)

For now we won't do anything with the PCC power leads (yellow/black) and
will connect them to the PCC in a future step.

## Connecting Buck Converters to PDB

With the VMC and PCC buck converters ready to go we will now connect them to the PDB
of the AVR drone. If you recall from before, the PDB sits in between the top and
bottom plates of the frame. **Remove the top plate of the frame to expose the PDB.**

After removing the top plate make sure to plug the VMC buck converter into the
female bullet connectors on the right side of the PDB. This will put the barrel
plug on the same side of the VMC input jack, after we mount it in a future step.

{{% alert title="Tip" color="tip" %}}
If you're wondering which side is the "right side",
we are referring to the right side with the nose of the AVR drone pointed away
from us and looking down on the frame.
{{% /alert %}}

{{% alert title="Note" color="note" %}}
Be sure to plug the red lead from the buck converter into the positive terminal
on the PDB. It will also be red as shown in the photo below. Then proceed
with black to black.
{{% /alert %}}

![VMC buck converter plugged into PDB](connect_vmc_buck_converter.jpg)

Repeat the process for the left side of the PDB, which will provide
power to the PCC buck converter.

![PCC buck converter plugged into PDB](pcc_buck_converter_pdb.jpg)

{{% alert title="Danger" color="danger" %}}
Please do not power your AVR drone until the PCC power leads (yellow/black)
have been connected. Otherwise you will run the risk of the leads creating a
short circuit since they are exposed. To be extra safe you can apply heat shrink
or electrical tape to the exposed wires.
{{% /alert %}}

## Remove Landing Gear

The buck converters will be mounted where the existing landing gear are attached.
It's much easier to remove the landing gear with the top plate removed,
so let's go ahead and do that. In the next section we will upgrade the landing gear,
which will provide plenty of clearance beneath the AVR drone. This will be very
important for the competition.

![Basic landing gear ready to be removed](landing_gear_attachment.jpg)

## Mounting Buck Converters

The final step is to attach the buck converters to the bottom plate of the
AVR drone frame. We recommend using a strong double-sided adhesive such as the
3M tape available at your local hardware store.

![Buck converters attached to bottom plate](buck_converters_attached.jpg)

{{% alert title="Tip" color="tip" %}}
Don't attach your top plate just yet! We need to keep it removed for the next section.
{{% /alert %}}
