#!/bin/bash

# run the linker because it couldnt do it at build time for some reason
ldconfig /opt/nvidia/vpi1/lib64

# run the python program (launches the C program)
python3.9 python/apriltag_processor.py
