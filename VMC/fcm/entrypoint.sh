#!/bin/bash 

sleep 10 #to allow sim to finish booting in case where running in sim

python fcc_telemetry.py & 

python fcc_control.py &

python fcc_hil_gps.py