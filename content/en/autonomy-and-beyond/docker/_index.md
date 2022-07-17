---
title: "Docker"
weight: 8
---

A Docker container is a lightweight executable package of a software that includes everything needed to run an application. In the AVR software package, parts of the code running on the Jetson(MQTT, AprilTag, Flight Control, etc.) are all run on individual Docker containers. You learned how to initialize and run them on the Jetson in the [software]({{< relref "software" >}}) section of this guide.

As a reminder, make sure to run the setup each time you want to pull the latest version of each of the modules.

```bash
cd ~/AVR-2022/VMC/scripts
git pull
./setup.py
```

To run the modules, use the start.py script.

```bash
cd ~/AVR-2022/VMC/
./start.py run
```

Your sandbox environment will be one of these modules. A basic sandbox.py script has been created for you. To run this specifically:

```bash
./start.py run sandbox
```

Each time you make changes/additions to your sandbox.py script, you will need to rebuild the module before running again.

```bash
./start.py build sandbox
```

{{% alert title="Done!" color="info" %}}
Nice work. You're now ready to start experimenting in the sandbox module!
{{% /alert %}}
