---
title: "Safety"
weight: 7
---

## Safety Setup

Previously, in the RC Transmitter Setup section, we covered 
[Setting Up Failsafe]({{< relref "../../rc-transmitter-setup/setting-up-failsafe" >}}). 
In QGC we need to make sure we disable some of the failsafe options, as many of 
them are related to GPS-enabled drones. VRC is all about indoor navigation in a 
GPS-denied environment therefore it warrants a different safety configuration. 
The video below walks through the setup process.

{{< youtube 8IWfmRFB6S8 >}}

## Disable Safety Switch

Bell VRC is about navigating indoors in a **GPS-denied** environment. 
In many cases, users of GPS-based drones have a safety switch to pre-arm their drone. 
Since we do not have the requirement of this hardware we will need to 
disable the pre-arm check.

To do this we will change one parameter in PX4's configuration known as 
**CBRK_IO_SAFETY**. You can find 
[all PX4 parameters here](https://docs.px4.io/v1.11/en/advanced_config/parameter_reference.html). 
It's not important to  understand all of these parameters, although it is 
important to understand  the process of changing them, as this will be necessary 
for Phase 2 of VRC.

In the video below we give an overview of why this parameter needs to be 
changed and how to do it. You will learn how to assign a value of **22027** 
(disabled) to **CBRK_IO_SAFETY**.

{{< youtube L5_IDcIgMcc >}}
