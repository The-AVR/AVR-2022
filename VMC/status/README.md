# Status Module

## Notes

-need to figure out a way to make lights automatically power off on docker down/stop. Might be possible with an entry point file. 
https://stackoverflow.com/questions/41451159/how-to-execute-a-script-when-i-terminate-a-docker-container
-Need to ensure nvpmodel is an executable  (added to setup script)

## Color Schema

Module:     Message:        LED:    Color:
VIO:        "vrc/vio"       1       PURPLE
PCM:        "vrc/pcm"       2       AQUA
Thermal:    "vrc/thermal"   3       BLUE
FCC:        "vrc/fcm"       4       ORANGE
AprilTag:   "vrc/apriltags" 5       YELLOW
