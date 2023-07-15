#!/bin/bash

/app/mavp2p udps:127.0.0.1:14540 tcps:0.0.0.0:5760 tcps:0.0.0.0:5761 udps:0.0.0.0:14541 --print-errors &

HEADLESS=1 make px4_sitl_default gazebo