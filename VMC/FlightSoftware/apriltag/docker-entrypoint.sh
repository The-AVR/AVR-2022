#!/bin/bash

# run the linker because it couldnt do it at build time for some reason
ldconfig /opt/nvidia/vpi1/lib64
# run the c program
python3 python/apriltag_processor.py
