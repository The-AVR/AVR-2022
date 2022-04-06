#!/bin/sh

/app/mavp2p serial:/dev/ttyTHS1:500000 tcps:0.0.0.0:5760 udpc:localhost:14541 udpc:localhost:14542 --print-errors
