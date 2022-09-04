---
title: "VMC and PCC Power"
weight: 1
---

Two main components of your advanced build are the **Vehicle Management Computer** (VMC), which runs the AVR software stack and the **Peripheral Control Computer** (PCC), which will allow teams to manually and programmatically control the LED ring, actuate up to four servos, and control the laser.

This section will walk through the necessary steps for providing adequate power to both the VMC and PCC.
This will be done with two separate buck converters.
The main battery of your AVR drone is 16.8V fully charged.
The required input voltage for the VMC and PCC are 5V, therefore the buck converters will step the voltage down to a usable 5V.

![Power Wiring Diagram](avr_power_wiring_diagram.jpg)

This section will work its way from the battery out to the VMC & PCC.

## Y-Cable

The Y-cable is the cable that splits the battery power into two directions: one for the ESC, and one for the PDB.

To create the wire cables use 3 of the 4 pre-soldered XT60 cables from the kit, 2 females and one male.

![XT60 cables](y_cable_layout_1.jpg)

![XT60 male (left) and female (right) connectors ](y_cable_male_female.jpg)

Firstly, cut each cable to approximately 1.5 inches and solder the ends so that they are ready to combine. The end result should look similar to the following.

![XT60 cables preparation](y_cable_layout_2.jpg)

Next, place heat shrink large enough to slide over the 3 cable solder joint on the side with 1 male connector. Then, solder the 3 ground (black) cables together.
Pull the heat shrink down over the end of the connection and apply heat.
If you have access to a heat gun or a lighter this will work well.
Alternatively, you can use the side of your soldering iron to apply heat and let the tubing shrink over your connectors.

![Soldering XT60 cables](y_cable_assy_1.jpg)

Repeat for the voltage (red) cables.

![Soldering XT60 cables](y_cable_assy_2.jpg)

Your finished cable should look like the photo below.

![Y cable with 1 male and 2 female connectors](y_cable_complete.jpg)

## Power Distribution Board (PDB)

Before installing the buck converters, the Power Distribution Board (PDB) will need to be soldered correctly. The PDB will allow us to split off power from the battery to each of the buck converters. The buck converters will step down the 16.8V from the battery to a usable 5V for both the VMC and PCC.

{{% alert title="Warning" color="warning" %}}
Soldering the larger pads on the PDB requires skill and patience. If possible, we recommend using a flat tip on your iron instead of the normal pointed tip. This will allow for much better heat transfer.
{{% /alert %}}

We recommend watching <a href="https://www.youtube.com/watch?v=GoPT69y98pY" target="_blank">this video that goes into great detail on soldering</a>. It's a lengthy video so at the very least you should scrub through it before attempting to solder your PDB.

You do not want the PDB to slide around while soldering. One of our favorite tricks is to use <a href="https://www.amazon.com/Blu-Tack-S050Q-Reusable-Adhesive-75g/dp/B001FGLX72" target="_blank">Blu Tack</a> to hold components in place.

Start the process by tinning the Batt +/- pads as shown in the photo below.

![Tinning PDB batt +/- pads](pdb_input_soldering_1.jpg)

![Pads tinned and ready for input wires](pdb_input_soldering_2.jpg)

![PDB, wires, and buck converters](power_overview.jpg)

The first step is to solder on the battery leads to the PDB.
To do this cut 1 male XT60 cable to about 1.5 inches and pre-tin the ends as we did with the y-cable above.

Cut the wires to make 4 \_**_8 or 6 or 4 inch_** wires; 2 black and 2 red. These will be used to connect the PDU to the ESC

Next, pre-tin the battery pads on the PDB

# TODO: Add image

Images of soldering on battery leads?
Possibly link to video?
This Guy is very thorough and i watched him when i was building mine...
I think he does say "fricken" at one point though, idk if that matters?
or if there is time for you to make a video that would be awesome,
but i know that is asking a lot.
https://youtu.be/GoPT69y98pY

Apply the soldering iron to the heat pad and start feeding the solder on to the ESC pad (do not the soldering iron itself, if the soldering pad is not heating up you can end up with cold soldering joints.)

![Soldering the PDB](pdu_solder_pads_1.jpg)

Once the pads are pre-tinned it should like the following.

![Pre-tinned Solder Pads](pdu_solder_pads_2.jpg)

Next, apply solder to the wires to pre-tin them.

![Pre-tinned Wires](pdu_pretin.jpg)

After pre-tinning everything, place the battery leads on the battery pad and push the soldering iron down on the top of the leads until it heats up the solder enough to start melting.
When doing this be sure to leave the iron on long enough so that the solder on the pad starts to heat up.

![Soldering wires to pads](pdu_solder_pads_3.jpg)

Repeat for the both wires.

After successfully soldering everything to the PDB, use a voltmeter to test and make ensure that there are no shorts between the positive and negative connections.

![Checking connections](pdu_verification.jpg)

Repeat for the second set of wires.

You should now be at a place where you have all the parts as shown in the following image.

![Power Distribution Layout](power_layout.jpg)

Place the PDU on top of the ESC standoffs and secure using M2.5 nuts from your AVR kit.

![Mounting the PDB](pdu_mounting.jpg)

Next route the wires through the middle plate and back out to the front of the drone.
This will keep wires tidy, out of the way of the battery once assembled, and ready for attachment to the buck converters.

## VMC Buck Converter

# TODO: update following section

Add images/instructions of PDB placement mounting/connection.

I have left this in place for reference of flow for now.

The following steps will be repeated for both buck converters and connected
to the PDB of the AVR drone.

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

![Apply heat shrink with a soldering iron](heat_shrink_soldering_iron.jpg)

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

# TODO: Delete the following sections

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
