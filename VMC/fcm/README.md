# AVR-VMC-FlightControl-Module

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)


The Flight Control module (FCM) is responsible for communicating with the
FCC over MAVLink. This module takes telemetry data from the FCC and publishes
it over MQTT. Additionally, it takes fake GPS data from the Fusion module
and feeds it to the FCC.

There also exists functionality to send commands to the FCC, such as arming the
drone, or sending it missions.


# MQTT Endpoints
Topic: `/avr/fcm/actions/`

### Arm

Schema: 
```json
{
    "action": "arm",
    "payload": {}
}
```

### Disarm

Schema: 
```json
{
    "action": "disarm",
    "payload": {}
}
```

### Kill 
Schema: 
```json
{
    "action": "kill",
    "payload": {}
}
```
### Land
Schema: 
```json
{
    "action": "land",
    "payload": {}
}
```
### Reboot
Schema: 
```json
{
    "action": "reboot",
    "payload": {}
}
```

### Go To Location
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

### Upload Mission
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
Schema: 
```json
{
    "action": "start_mission",
    "payload": {}
}
```