import asyncio
import math
import time
from typing import Any, Callable, List

import mavsdk
from bell.avr.mqtt.client import MQTTModule
from bell.avr.mqtt.payloads import (
    AvrFcmAttitudeEulerPayload,
    AvrFcmBatteryPayload,
    AvrFcmEventsPayload,
    AvrFcmGpsInfoPayload,
    AvrFcmLocationGlobalPayload,
    AvrFcmLocationHomePayload,
    AvrFcmLocationLocalPayload,
    AvrFcmStatusPayload,
    AvrFcmVelocityPayload,
)
from bell.avr.utils.decorators import async_try_except, try_except
from bell.avr.utils.timing import rate_limit
from loguru import logger
from fcc_mqtt import FCMMQTTModule
import sys


class TelemetryManager(FCMMQTTModule):
    def __init__(self) -> None:
        super().__init__()

        # mavlink stuff
        self.drone = mavsdk.System(sysid=142)

        # current state of offboard mode, acts as a backup for PX4
        self.offboard_enabled = False

        # telemetry persistent variables
        self.in_air: bool = False
        self.is_armed: bool = False
        self.fcc_mode = "UNKNOWN"
        self.heading = 0.0

    async def connect(self) -> None:
        """
        Connect the Drone object.
        """
        logger.debug("Telemetry: Connecting to the FCC")

        # un-comment to show mavsdk server logging
        # import logging
        # logging.basicConfig(level=logging.DEBUG)

        # mavsdk does not support dns
        await self.drone.connect(system_address="tcp://127.0.0.1:5761")

        logger.success("Telemetry: Connected to the FCC")
        self._publish_event("fcc_telemetry_connected_event")


    async def run_non_blocking(self) -> asyncio.Future:
        """
        Run the Flight Control Computer module
        """
        # start our MQTT client
        super().run_non_blocking()

        # connect to the fcc
        await self.connect()

        # start tasks
        return asyncio.gather(
            self.telemetry_tasks(),
        )
    
    async def run(self) -> asyncio.Future:
        asyncio.gather(self.run_non_blocking())
        while True:
            await asyncio.sleep(1)

    # region ###################  T E L E M E T R Y ###########################

    async def telemetry_tasks(self) -> asyncio.Future:
        """
        Gathers the telemetry tasks
        """
        return asyncio.gather(
            self.connected_status_telemetry(),
            self.battery_telemetry(),
            self.in_air_telemetry(),
            self.is_armed_telemetry(),
            self.flight_mode_telemetry(),
            self.landed_state_telemetry(),
            self.position_ned_telemetry(),
            self.position_lla_telemetry(),
            self.home_lla_telemetry(),
            self.attitude_euler_telemetry(),
            self.velocity_ned_telemetry(),
            self.gps_info_telemetry(),
        )

    @async_try_except()
    async def connected_status_telemetry(self) -> None:
        """
        Runs the connected_status telemetry loop
        """
        was_connected = False
        flip_time = time.time()
        debounce_time = 2

        logger.debug("connected_status loop started")
        async for connection_status in self.drone.core.connection_state():
            connected = connection_status.is_connected
            now = time.time()
            should_update = False

            # every time the state changes, record that time
            if connected != was_connected:
                should_update = True
                flip_time = time.time()

            # if the state has been steady for debounce_time
            if (now - flip_time > debounce_time) and should_update:
                if connected:
                    self._publish_event("fcc_telemetry_connected_event")
                else:
                    self._publish_event("fcc_telemetry_disconnected_event")
                should_update = False

            was_connected = connected

    @async_try_except()
    async def battery_telemetry(self) -> None:
        """
        Runs the battery telemetry loop
        """
        logger.debug("battery_telemetry loop started")
        async for battery in self.drone.telemetry.battery():

            update = AvrFcmBatteryPayload(
                voltage=battery.voltage_v,
                soc=battery.remaining_percent * 100.0,
            )
            self.send_message("avr/fcm/battery", update) #type: ignore

    @async_try_except()
    async def in_air_telemetry(self) -> None:
        """
        Runs the in_air telemetry loop
        """
        logger.debug("in_air loop started")
        async for in_air in self.drone.telemetry.in_air():
            self.in_air = in_air

    @async_try_except()
    async def is_armed_telemetry(self) -> None:
        """
        Runs the is_armed telemetry loop
        """
        was_armed = False
        logger.debug("is_armed loop started")
        async for armed in self.drone.telemetry.armed():

            # if the arming status is different than last time
            if armed != was_armed:
                if armed:
                    self._publish_event("fcc_armed_event")
                else:
                    self._publish_event("fcc_disarmed_event")
            was_armed = armed
            self.is_armed = armed

            update = AvrFcmStatusPayload(
                armed=armed,
                mode=str(self.fcc_mode),
            )

            self.send_message("avr/fcm/status", update) #type: ignore

    @async_try_except()
    async def landed_state_telemetry(self) -> None:
        """
        Runs the landed state loop, returns one of:
        IN_AIR,LANDING,ON_GROUND,TAKING_OFF, or UNKNOWN
        """
        previous_state = "UNKNOWN"

        async for state in self.drone.telemetry.landed_state():
            mode = str(state)
            # if we have a state change
            if mode != previous_state:
                if mode == "IN_AIR":
                    self._publish_event("landed_state_in_air_event")
                elif mode == "LANDING":
                    self._publish_event("landed_state_landing_event")
                elif mode == "ON_GROUND":
                    self._publish_event("landed_state_on_ground_event")
                elif mode == "TAKING_OFF":
                    self._publish_event("landed_state_taking_off_event")
                elif mode == "UNKNOWN":
                    self._publish_event("landed_state_unknown_event")
            previous_state = mode

    @async_try_except()
    async def flight_mode_telemetry(self) -> None:
        """
        Runs the flight_mode telemetry loop
        """
        fcc_mode_map = {
            "UNKNOWN": "fcc_unknown_mode_event",
            "READY": "fcc_ready_mode_event",
            "TAKEOFF": "fcc_takeoff_mode_event",
            "HOLD": "fcc_hold_mode_event",
            "MISSION": "fcc_mission_mode_event",
            "RETURN_TO_LAUNCH": "fcc_rtl_mode_event",
            "LAND": "fcc_land_mode_event",
            "OFFBOARD": "fcc_offboard_mode_event",
            "FOLLOW_ME": "fcc_follow_mode_event",
            "MANUAL": "fcc_manual_mode_event",
            "ALTCTL": "fcc_alt_mode_event",
            "POSCTL": "fcc_pos_mode_event",
            "ACRO": "fcc_acro_mode_event",
            "STABILIZED": "fcc_stabilized_mode_event",
            "RATTITUDE": "fcc_rattitude_mode_event",
        }

        fcc_mode = "UNKNOWN"

        logger.debug("flight_mode_telemetry loop started")

        async for mode in self.drone.telemetry.flight_mode():

            update = AvrFcmStatusPayload(
                mode=str(mode),
                armed=self.is_armed,
            )

            self.send_message("avr/fcm/status", update) #type: ignore

            if mode != fcc_mode:
                if mode in fcc_mode_map:
                    self._publish_event(fcc_mode_map[str(mode)])
                else:
                    self._publish_event("fcc_mode_error_event")

            fcc_mode = mode
            self.fcc_mode = mode

    @async_try_except()
    async def position_ned_telemetry(self) -> None:
        """
        Runs the position_ned telemetry loop
        """
        logger.debug("position_ned telemetry loop started")
        async for position in self.drone.telemetry.position_velocity_ned():

            n = position.position.north_m
            e = position.position.east_m
            d = position.position.down_m

            update = AvrFcmLocationLocalPayload(dX=n, dY=e, dZ=d)

            self.send_message("avr/fcm/location/local", update) #type: ignore

    @async_try_except()
    async def position_lla_telemetry(self) -> None:
        """
        Runs the position_lla telemetry loop
        """
        logger.debug("position_lla telemetry loop started")
        async for position in self.drone.telemetry.position():
            update = AvrFcmLocationGlobalPayload(
                lat=position.latitude_deg,
                lon=position.longitude_deg,
                alt=position.relative_altitude_m,
                hdg=self.heading,
            )

            self.send_message("avr/fcm/location/global", update) #type: ignore

    @async_try_except()
    async def home_lla_telemetry(self) -> None:
        """
        Runs the home_lla telemetry loop
        """
        logger.debug("home_lla telemetry loop started")
        async for home_position in self.drone.telemetry.home():
            update = AvrFcmLocationHomePayload(
                lat=home_position.latitude_deg,
                lon=home_position.longitude_deg,
                alt=home_position.relative_altitude_m,
            )

            self.send_message("avr/fcm/location/home", update) #type: ignore

    @async_try_except()
    async def attitude_euler_telemetry(self) -> None:
        """
        Runs the attitude_euler telemetry loop
        """

        logger.debug("attitude_euler telemetry loop started")
        async for attitude in self.drone.telemetry.attitude_euler():
            psi = attitude.roll_deg
            theta = attitude.pitch_deg
            phi = attitude.yaw_deg

            # do any necessary wrapping here
            update = AvrFcmAttitudeEulerPayload(
                roll=psi,
                pitch=theta,
                yaw=phi,
            )

            heading = (2 * math.pi) + phi if phi < 0 else phi
            heading = math.degrees(heading)

            self.heading = heading

            # publish telemetry every tenth of a second
            rate_limit(
                lambda: self.send_message("avr/fcm/attitude/euler", update), #type: ignore
                frequency=10,
            )

    @async_try_except()
    async def velocity_ned_telemetry(self) -> None:
        """
        Runs the velocity_ned telemetry loop
        """

        logger.debug("velocity_ned telemetry loop started")
        async for velocity in self.drone.telemetry.velocity_ned():
            update = AvrFcmVelocityPayload(
                vX=velocity.north_m_s,
                vY=velocity.east_m_s,
                vZ=velocity.down_m_s,
            )

            self.send_message("avr/fcm/velocity", update) #type: ignore

    @async_try_except()
    async def gps_info_telemetry(self) -> None:
        """
        Runs the gps_info telemetry loop
        """
        logger.debug("gps_info telemetry loop started")
        async for gps_info in self.drone.telemetry.gps_info():
            update = AvrFcmGpsInfoPayload(
                num_satellites=gps_info.num_satellites,
                fix_type=str(gps_info.fix_type),
            )

            self.send_message("avr/fcm/gps_info", update) #type: ignore

    # endregion ###############################################################

if __name__ == "__main__":
    telemetry = TelemetryManager()
    asyncio.run(telemetry.run())

