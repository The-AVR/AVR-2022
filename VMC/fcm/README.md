# AVR-VMC-FlightControl-Module

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)


The Flight Control module (FCM) is responsible for communicating with the
FCC over MAVLink. This module takes telemetry data from the FCC and publishes
it over MQTT. Additionally, it takes fake GPS data from the Fusion module
and feeds it to the FCC.

There also exists functionality to send commands to the FCC, such as arming the
drone, or sending it missions.


# MQTT Endpoints
Topic: `avr/fcm/capture_home`

Schema: `{}`

Captures the "home" position that represents 0,0,0 in the NED reference frame.
By default, the drone will capture this position as soon as the FCM receives data about its location.
It is a *prudent* idea to manually trigger this once you have placed the drone on the starting pad.

Topic: `/avr/fcm/actions`

### Arm
Description: Arms the drone

Schema:
```json
{
    "action": "arm",
    "payload": {}
}
```

### Disarm
Description: Disarms the drone

Schema:
```json
{
    "action": "disarm",
    "payload": {}
}
```

### Kill
Description: Similar to disarm, however this will force stop the motors even if PX4 is airborne. This is an EMERGENCY only action that could result in damage to your drone if not used appropriately.

Schema:
```json
{
    "action": "kill",
    "payload": {}
}
```
### Land

Description: Requests the drone to land in place

Schema:
```json
{
    "action": "land",
    "payload": {}
}
```
### Reboot

Description: Reboots the flight controller

Schema:
```json
{
    "action": "reboot",
    "payload": {}
}
```

### Go To Location

Description: Sends the drone to the location prescribed by lat/lon/alt. The drone will fly a straight line to this point while pointing its nose in the `heading` direction.

Schema:
```json
{
    "action": "goto_location",
    "payload": {
        "lat": <decimal_degrees_lat>,
        "lon": <decimal_degrees_lon>,
        "alt": <float_meters_MSL>,
        "heading": <decimal degrees heading>
    }
}
```

### Go To Location NED

Description: Sends the drone to the location prescribed by n/e/d relative to the "home" position. The drone will fly a straight line to this point while pointing its nose in the direction of the point.

Schema:
```json
{
    "action": "goto_location_ned",
    "payload": {
        "n": <decimal_meters_north>,
        "e": <decimal_meters_east>,
        "d": <decimal_meters_*down*>,
        "heading": <decimal degrees heading>
    }
}
```

### Upload Mission

Description: Upload a mission to the flight controller. Waypoints can be one of `goto`, `takeoff`, or `land`. The waypoints use latitude, longitude, and relative altitude (from the drones "home" position, which can be manually updated by sending a message to avr/fcm/capture_home. Home is automatically captured on FCM boot so make sure you capture home before taking off for the first time. Waypoints can optionally use the `n` `e` `d` paradigm, in which missions are defined in the NED coordinate system relative to the home position.

Schema:
```json
{
    "action": "upload_mission",
    "payload": {
        "waypoints": [
    {
        "type": "goto",
        "lat": <decimal_degrees_lat>,
        "lon": <decimal_degrees_lon>,
        "alt": <float_meters_relative_takeoff>,
    },
    {
        "type": "goto",
        "lat": <decimal_degrees_lat>,
        "lon": <decimal_degrees_lon>,
        "alt": <float_meters_relative_takeoff>,
    }
]
    }
}
```

### Start Mission

Description: Requests the drone to start the mission.

Schema:
```json
{
    "action": "start_mission",
    "payload": {}
}
```
