---
title: "Running VMC Software"
weight: 3
---

## Networking

Before running the VMC software, we highly recommend that you configure
the Jetson to act as it's own WiFi network you can connect to. To do this,
login to the Jetson, go into the "VMC" directory,
and run the command `./scripts/wifi.py create`:

```bash
cd ~/AVR-2022/VMC/
./scripts/wifi.py create
```

This will walk you through creating a WiFi network that you can connect to.

![WiFi setup wizard](2022-06-15-19-06-22.png)

{{% alert title="Tip" color="tip" %}}

You can also use the the `disconnect` command to disconnect from all WiFi networks
and disable the hotspot, or the `connect` command to more easily connect to an
existing WiFi network.

![Disconnect/Connect to WiFi networks](2022-06-15-19-08-45.png)

{{% /alert %}}

After connecting to the WiFi network, your Jetson will _always_ have the IP address
`10.42.0.1`, which you can use to
[connect to via SSH]({{< relref "../connecting-to-the-jetson/#ssh" >}}).

## Running

After connecting to your Jetson via the hotspot, go into the "VMC" directory,
and run the command `./start.py run`:

```bash
cd ~/AVR-2022/VMC/
./start.py run
```

![](2022-06-14-21-03-51.png)

To shutdown the software, press <kbd>Ctrl</kbd>+<kbd>C</kbd> in the console
window you started the software in. Additionally, run

```bash
./start.py stop
```

for good measure.

![](2022-06-14-21-06-25.png)

## Options

With the basics out of the way, there are some options that can be used
to control which parts of the software are run. By default, a normal set of modules
are run:

```bash
./start.py run
# also equivalent to
./start.py run --norm
./start.py run -n
```

- fcm
- fusion
- mavp2p
- mqtt
- vio
- apriltag
- pcm
- status
- thermal

However, let's say you have just the bare minimum equipment installed on your drone
(just the ZED Mini camera). You can use the `--min` option to run only the
following modules which are the bare minimum required for flight:

```bash
./start.py run --min
# also equivalent to
./start.py run -m
```

- fcm
- fusion
- mavp2p
- mqtt
- vio

On the other hand, if you have everything installed, and also
want to run your own code in the sandbox module you can use the `--all` option:

```bash
./start.py run --all
# also equivalent to
./start.py run -a
```

- fcm
- fusion
- mavp2p
- mqtt
- vio
- apriltag
- pcm
- status
- thermal
- sandbox

Lastly, if you want to run modules not defined in a preset here, you can either
list them all out explicitly, or add the additional modules you want to an exisiting
alias:

```bash
# the following are equivalent
./start.py run pcm --min # the --min must come at the end
./start.py run fcm vio mqtt mavp2p fusion pcm
```

If you ever need help, just add the `--help` argument to the command:

```text
usage: start.py [-h] [-l] [-m | -n | -a] {run,build,pull,stop} [modules ...]

positional arguments:
  {run,build,pull,stop}
                        Action to perform
  modules               Explicitly list which module(s) to perform the action one

optional arguments:
  -h, --help            show this help message and exit
  -l, --local           Build containers locally rather than using pre-built ones from GitHub
  -m, --min             Perform action on minimal modules (fcm, fusion, mavp2p, mqtt, vio). Adds to any modules explicitly specified.
  -n, --norm            Perform action on normal modules (apriltag, fcm, fusion, mavp2p, mqtt, pcm, status, thermal, vio). Adds to any modules explicitly specified. If nothing else is specified, this
                        is the default.
  -a, --all             Perform action on all modules (apriltag, fcm, fusion, mavp2p, mqtt, pcm, sandbox, status, thermal, vio). Adds to any modules explicitly specified.
```

## Troubleshooting

Sometimes when starting the AVR software, things don't all start correctly.

### Cannot start service pcm

Example output:

```text
Needing sudo privileges to run docker, re-launching
Running command: docker-compose --project-name AVR-2022 --file /tmp/docker-compose-v5eqlg13.yml up --remove-orphans --force-recreate pcm
/usr/local/lib/python3.6/dist-packages/paramiko/transport.py:33: CryptographyDeprecationWarning: Python 3.6 is no longer supported by the Python core team. Therefore, support for it is deprecated in cryptography and will be removed in a future release.
  from cryptography.hazmat.backends import default_backend
Creating network "avr-2022_default" with the default driver
Creating avr-2022_mqtt_1 ... done
Creating avr-2022_pcm_1  ... error

ERROR: for avr-2022_pcm_1  Cannot start service pcm: error gathering device information while adding custom device "/dev/ttyACM0": no such file or directory

ERROR: for pcm  Cannot start service pcm: error gathering device information while adding custom device "/dev/ttyACM0": no such file or directory
ERROR: Encountered errors while bringing up the project.
```

This error means that the AVR software was unable to connect to the PCC.
If you are not using the PCC, follow the steps above to disable that module.

Otherwise, to test that the PCC is correctly connected to the VMC, run the command:

```bash
ls /dev/ttyACM0
```

You'll get the message `ls: cannot access '/dev/ttyACM0': No such file or directory`
if the PCC is not connected. If the PCC is connected,
`/dev/ttyACM0` will get echoed back.
Try unplugging the PCC and plugging it back into the VMC.
