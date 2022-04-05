#!/bin/bash
sudo modprobe spidev
sudo docker compose -f docker-compose-dev.yml up

