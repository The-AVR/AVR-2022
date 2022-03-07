#!/bin/sh

/app/mavp2p serial:/dev/ttyTHS1:500000 tcps:0.0.0.0:5760 udpc:127.0.0.1:14541 udpc:127.0.0.1:14542 --print-errors
