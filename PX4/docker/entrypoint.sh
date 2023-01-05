#!/bin/bash
# python3 /root/.local/bin/mavproxy.py --daemon --master=udpin:127.0.0.1:14550 --out=tcpin:0.0.0.0:5760 2>&1 > /dev/null &
# python3 /root/.local/bin/mavproxy.py --daemon --master=tcpin:127.0.0.1:4560 --out=tcpout:host.docker.internal:4560 2>&1 > /dev/null &
python3 /root/.local/bin/mavproxy.py --daemon --master=udpin:127.0.0.1:14550 --out=udpout:mavp2p:14540 2>&1 > /dev/null &
export PX4_SIM_HOST_ADDR=172.26.0.1
cat /Firmware/ROMFS/px4fmu_common/init.d-posix/px4-rc.mavlink
make px4_sitl_default none_iris