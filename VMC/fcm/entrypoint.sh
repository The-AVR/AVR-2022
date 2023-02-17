#!/bin/bash 

python fcc_telemetry.py & 

python fcc_control.py &

python fcc_hil_gps.py