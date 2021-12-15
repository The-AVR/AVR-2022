---
title: "Sandbox"
weight: 2
---

For teams that want to write their own code to run on their drone,
we recommend doing so through the "vrc_sandbox" in the Phase II repo:
[https://github.com/bellflight/VRC-2022/tree/main/VMC/FlightSoftware/sandbox](https://github.com/bellflight/VRC-2022/tree/main/VMC/FlightSoftware/sandbox).
This has already been configured to be very simple to get started with.

1. Edit the contents of `VMC/FlightSoftware/sandbox/sandbox.py` with your desired code.
   Read the comments within the file to understand what's going on
2. Un-comment the sandbox module from the `docker-compose.yml` file to enable it
   with the rest of the VMC software
3. Run `sudo docker-compose build sandbox` to ensure the built Docker
   container contains the latest version of your code

![](image.png)

With that, you can start the VRC software like normal!
Your code will run alongside the rest of the VMC modules.
