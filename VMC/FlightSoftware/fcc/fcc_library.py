import asyncio
import datetime
import functools
import json
import math
import queue
import time
from typing import Any, Callable, List

import mavsdk
from loguru import logger
from mavsdk.action import ActionError
from mavsdk.geofence import Point, Polygon
from mavsdk.mission_raw import MissionItem, MissionRawError
from mavsdk.offboard import VelocityBodyYawspeed, VelocityNedYaw
from paho.mqtt.client import Client as MQTTClient
from pymavlink import mavutil

# decorators


def try_except(reraise: bool = False):
    """
    Function decorator that acts as a try/except block around the function.

    Effectively equivalent to:

    ```python
    try:
        func()
    except Exception as e:
        print(e)
    ```

    Can optionally reraise the exception.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.exception(f"Unexpected exception in {func.__name__}")
                if reraise:
                    raise e

        return wrapper

    return decorator


def async_try_except(reraise: bool = False):
    """
    Same as `try_except()` function, just for async functions.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.exception(f"Unexpected exception in {func.__name__}")
                if reraise:
                    raise e

        return wrapper

    return decorator


# classes


class MAVMQTTBase:
    def __init__(self, client: MQTTClient, drone: mavsdk.System = None) -> None:
        self.drone = drone
        self.mqtt_client = client

        self.topic_prefix = "vrc/fcc"

    def _timestamp(self) -> str:
        return datetime.datetime.now().isoformat()

    @try_except()
    def _publish_event(self, name: str, payload: str = "") -> None:
        """
        Create and publish state machine event.
        """
        event = {}

        event["name"] = name
        event["payload"] = payload
        event["timestamp"] = self._timestamp()

        self.mqtt_client.publish(
            f"{self.topic_prefix}/events", json.dumps(event), retain=False, qos=0
        )

    async def async_queue_action(
        self, queue_: queue.Queue, action: Callable, frequency: int = 10
    ) -> None:
        """
        Creates a while loop that continously tries to pull a protobuf from a queue
        and do something with it at a set frequency.

        The given function needs to accept a single argument of the protobuf object
        and be async.

        Setting the frequency to 0 will always run the action.
        """
        last_time = time.time()

        # this particular design will constantly get messages from the queue,
        # even if they are not used, just to try and process them as fast
        # as possible to prevent the queue from filling

        while True:
            try:
                # get the next item from the queue
                data = queue_.get_nowait()
                # if the frequency is 0, or the time since our last run is greater
                # than the frequency, run
                if frequency == 0 or time.time() - last_time > (1 / frequency):
                    # call function
                    await action(data)
                    # reset timer
                    last_time = time.time()
            except queue.Empty:
                # if the queue was empty, just wait
                await asyncio.sleep(0.01)
            except Exception as e:
                logger.exception("Unexpected error in async_queue_action")


class FCC(MAVMQTTBase):
    def __init__(
        self,
        drone: mavsdk.System,
        client: MQTTClient,
        action_queue: queue.Queue,
        offboard_ned_queue: queue.Queue,
        offboard_body_queue: queue.Queue,
    ) -> None:
        super().__init__(client, drone)

        # this is solely for type hinting
        self.drone: mavsdk.System

        self.mission_api = MissionAPI(drone, client)

        # queues
        self.action_queue = action_queue
        self.offboard_ned_queue = offboard_ned_queue
        self.offboard_body_queue = offboard_body_queue

        # current state of offboard mode, acts as a backup for PX4
        self.offboard_enabled = False

        # telemetry
        self.in_air = False
        self.is_armed = False
        self.fcc_mode = "UNKNOWN"
        self.connected = False
        self.heading = 0.0

    async def connect(self) -> None:
        """
        Connect the Drone object.
        """
        await self.drone.connect(system_address="udp://:14541")

    # region ###################  T E L E M E T R Y ###########################

    async def telemetry_tasks(self) -> asyncio.Future:
        """
        Gathers the telemetry tasks
        """
        return asyncio.gather(
            # self.connected_status_telemetry(),
            self.battery_telemetry(),
            # self.in_air_telemetry(),
            self.is_armed_telemetry(),
            self.flight_mode_telemetry(),
            self.landed_state_telemetry(),
            # self.position_ned_telemetry(),
            self.position_lla_telemetry(),
            # self.home_lla_telemetry(),
            self.attitude_euler_telemetry(),
            self.velocity_ned_telemetry(),
        )

    @async_try_except()
    async def connected_status_telemetry(self) -> None:
        """
        Runs the connected_status telemetry loop
        """
        was_connected = False
        flip_time = time.time()
        debounce_time = 2

        logger.debug(f"connected_status loop started")
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
                    self._publish_event("fcc_connected_event")
                else:
                    self._publish_event("fcc_disconnected_event")
                should_update = False

            was_connected = connected

    @async_try_except()
    async def battery_telemetry(self) -> None:
        """
        Runs the battery telemetry loop
        """
        logger.debug(f"battery_telemetry loop started")
        async for battery in self.drone.telemetry.battery():

            update = {}
            update["voltage"] = battery.voltage_v * 4 #bc 4 cell
            # TODO see if mavsdk supports battery current
            # TODO see is mavsdk supports power draw
            update["soc"] = battery.remaining_percent * 100.0
            update["timestamp"] = self._timestamp()

            self.mqtt_client.publish(
                f"{self.topic_prefix}/battery", json.dumps(update), retain=False, qos=0
            )

    @async_try_except()
    async def in_air_telemetry(self) -> None:
        """
        Runs the in_air telemetry loop
        """
        logger.debug(f"in_air loop started")
        async for in_air in self.drone.telemetry.in_air():
            self.in_air = in_air

    @async_try_except()
    async def is_armed_telemetry(self) -> None:
        """
        Runs the is_armed telemetry loop
        """
        was_armed = False
        logger.debug(f"is_armed loop started")
        async for armed in self.drone.telemetry.armed():

            # if the arming status is different than last time
            if armed != was_armed:
                if armed:
                    self._publish_event("fcc_armed_event")
                else:
                    self._publish_event("fcc_disarmed_event")
            was_armed = armed
            self.is_armed = armed

            update = {}

            update["armed"] = armed
            update["mode"] = str(self.fcc_mode)
            update["timestamp"] = self._timestamp()

            self.mqtt_client.publish(
                f"{self.topic_prefix}/status", json.dumps(update), retain=False, qos=0
            )

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

        logger.debug(f"flight_mode_telemetry loop started")

        async for mode in self.drone.telemetry.flight_mode():

            update = {}

            update["mode"] = str(mode)
            update["armed"] = self.is_armed
            update["timestamp"] = self._timestamp()

            self.mqtt_client.publish(
                f"{self.topic_prefix}/status", json.dumps(update), retain=False, qos=0
            )

            if mode != fcc_mode:
                if mode in fcc_mode_map.keys():
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
        logger.debug(f"position_ned telemetry loop started")
        async for position in self.drone.telemetry.position_velocity_ned():

            n = position.position.north_m
            e = position.position.east_m
            d = position.position.down_m

            update = {}

            update["dX"] = n
            update["dY"] = e
            update["dZ"] = d
            update["timestamp"] = self._timestamp()

            self.mqtt_client.publish(
                f"{self.topic_prefix}/location/local",
                json.dumps(update),
                retain=False,
                qos=0,
            )

    @async_try_except()
    async def position_lla_telemetry(self) -> None:
        """
        Runs the position_lla telemetry loop
        """
        logger.debug(f"position_lla telemetry loop started")
        async for position in self.drone.telemetry.position():
            update = {}
            update["lat"] = position.latitude_deg
            update["lon"] = position.longitude_deg
            update["alt"] = position.relative_altitude_m
            update["hdg"] = self.heading
            update["timestamp"] = self._timestamp()

            self.mqtt_client.publish(
                f"{self.topic_prefix}/location/global",
                json.dumps(update),
                retain=False,
                qos=0,
            )

    @async_try_except()
    async def home_lla_telemetry(self) -> None:
        """
        Runs the home_lla telemetry loop
        """
        logger.debug(f"home_lla telemetry loop started")
        async for home_position in self.drone.telemetry.home():
            update = {}
            update["lat"] = home_position.latitude_deg
            update["lon"] = home_position.longitude_deg
            update["alt"] = home_position.relative_altitude_m  # agl
            update["timestamp"] = self._timestamp()

            self.mqtt_client.publish(
                f"{self.topic_prefix}/location/home",
                json.dumps(update),
                retain=False,
                qos=0,
            )

    @async_try_except()
    async def attitude_euler_telemetry(self) -> None:
        """
        Runs the attitude_euler telemetry loop
        """

        logger.debug(f"attitude_euler telemetry loop started")
        async for attitude in self.drone.telemetry.attitude_euler():
            # logger.debug( str(attitude))

            psi = attitude.roll_deg
            theta = attitude.pitch_deg
            phi = attitude.yaw_deg

            # TODO data validation?

            # do any necessary wrapping here
            update = {}

            update["roll"] = psi
            update["pitch"] = theta
            update["yaw"] = phi
            update["timestamp"] = self._timestamp()

            if phi < 0:
                heading = (2 * math.pi) + phi
            else:
                heading = phi

            heading = math.degrees(heading)

            self.heading = heading

            # publish the attitude
            self.mqtt_client.publish(
                f"{self.topic_prefix}/attitude/euler",
                json.dumps(update),
                retain=False,
                qos=0,
            )

    @async_try_except()
    async def velocity_ned_telemetry(self) -> None:
        """
        Runs the velocity_ned telemetry loop
        """

        logger.debug(f"velocity_ned telemetry loop started")
        async for velocity in self.drone.telemetry.velocity_ned():
            update = {}

            update["vX"] = velocity.north_m_s
            update["vY"] = velocity.east_m_s
            update["vZ"] = velocity.down_m_s
            update["timestamp"] = self._timestamp()

            self.mqtt_client.publish(
                f"{self.topic_prefix}/velocity", json.dumps(update), retain=False, qos=0
            )

    # endregion ###############################################################

    # region ################## D I S P A T C H E R  ##########################

    @async_try_except()
    async def action_dispatcher(self) -> None:
        class DispatcherBusy(Exception):
            """
            Exception for when the action dispatcher is currently busy
            executing another action
            """

        class DispatcherManager(MAVMQTTBase):
            def __init__(self, client: MQTTClient) -> None:
                super().__init__(client)
                self.currently_running_task = None
                self.timeout = 10

            async def schedule_task(self, task: Callable, payload: Any, name: str):
                """
                Schedule a task (async func) to be run by the dispatcher with the
                given payload. Task name is also required for printing.
                """
                logger.debug(f"Scheduling a task for '{name}'")
                # if the dispatcher is ok to take on a new task
                if self.currently_running_task is None:
                    await self.create_task(task, payload, name)
                # or if there is already a running task
                else:  # see if the task is done
                    if self.currently_running_task.done():
                        await self.create_task(task, payload, name)
                    # or tell the caller to go away
                    else:
                        raise DispatcherBusy

            async def create_task(self, task: Callable, payload: dict, name: str):
                """
                Create a task to be run.
                """
                self.currently_running_task = asyncio.create_task(
                    self.task_waiter(task, payload, name)
                )

            async def task_waiter(self, task: Callable, payload: dict, name: str):
                """
                Execute a task with a timeout.
                """
                try:
                    await asyncio.wait_for(task(**payload), timeout=self.timeout)
                    self._publish_event(
                        "request_" + name + "_completed_event"
                    )
                    # Logging.normal(prefix, f"Task '{name}' returned")
                    self.currently_running_task = None

                except asyncio.TimeoutError:
                    try:
                        logger.warning(f"Task '{name}' timed out!")
                        self._publish_event("action_timeout_event", name)
                        self.currently_running_task = None
                    except Exception as e:
                        logger.exception("ERROR IN TIMEOUT HANDLER")
                except Exception as e:
                    logger.exception("ERROR IN TASK WAITER")

        logger.debug(f"action_dispatcher started")

        action_map = {
            "break": self.set_intentional_timeout,
            "connect": self.connect,
            "arm": self.set_arm,
            "disarm": self.set_disarm,
            "kill": self.set_kill,
            "land": self.set_land,
            "reboot": self.set_reboot,
            "takeoff": self.set_takeoff,
            "offboard_start": self.offboard_start,
            "offboard_stop": self.offboard_stop,
            "upload_mission": self.upload_mission,
            "begin_mission": self.begin_mission,
            "pause_mission": self.pause_mission,
            "resume_mission": self.resume_mission,
        }

        dispatch = DispatcherManager(self.mqtt_client)

        while True:
            try:
                # TODO - Casey, 6/27 start here and make action into a dict instead of proto
                action = self.action_queue.get_nowait()

                if action["payload"] == "":
                    # Logging.normal(prefix,"Creating empty JSON string because payload was empty")
                    action["payload"] = "{}"

                if action["name"] in action_map:
                    payload = json.loads(action["payload"])
                    await dispatch.schedule_task(
                        action_map[action["name"]], payload, action["name"]
                    )
            except DispatcherBusy:
                logger.info("I'm busy running another task, try again later")
                self._publish_event("fcc_busy_event", payload=action["name"])
            except queue.Empty:
                await asyncio.sleep(0.1)
            except Exception as e:
                logger.exception("ERROR IN MAIN LOOP")

    async def simple_action_executor(
        self,
        action_fn: Callable,
        action_text: str,
    ) -> None:
        """
        Executes a given async action function, and publishes a success or failed
        state machine event given whether or not an `ActionError` was raised.
        """
        try:
            await action_fn()
            full_success_str = action_text + "_success_event"
            logger.info(f"Sending {full_success_str}")
            self._publish_event(full_success_str)
        except ActionError as e:
            full_fail_str = action_text + "_failed_event"
            logger.info(f"Sending {full_fail_str}")
            self._publish_event(full_fail_str)
            if e._result.result_str == "CONNECTION_ERROR":
                asyncio.create_task(self.connect())
            raise e

    # endregion ###############################################################

    # region #####################  A C T I O N S #############################

    @async_try_except()
    async def set_intentional_timeout(self, **kwargs) -> None:
        """
        Sets a 20 second timeout.
        """
        try:
            await asyncio.sleep(20)
        except asyncio.CancelledError:
            pass

    @async_try_except(reraise=True)
    async def set_arm(self, **kwargs) -> None:
        """
        Sets the drone to an armed state.
        """
        logger.info("Sending arm command")
        await self.simple_action_executor(self.drone.action.arm, "arm")

    @async_try_except(reraise=True)
    async def set_disarm(self, **kwargs) -> None:
        """
        Sets the drone to a disarmed state.
        """
        logger.info("Sending disarm command")
        await self.simple_action_executor(self.drone.action.disarm, "disarm")

    @async_try_except(reraise=True)
    async def set_kill(self, **kwargs) -> None:
        """
        Sets the drone to a kill state. This will forcefully shut off the drone
        regardless of being in the air or not.
        """
        logger.warning("Sending kill command")
        await self.simple_action_executor(self.drone.action.kill, "kill")

    @async_try_except(reraise=True)
    async def set_land(self, **kwargs) -> None:
        """
        Commands the drone to land at the current position.
        """
        logger.info("Sending land command")
        await self.simple_action_executor(self.drone.action.land, "land_cmd")

    @async_try_except(reraise=True)
    async def set_reboot(self, **kwargs) -> None:
        """
        Commands the drone computer to reboot.
        """
        logger.warning("Sending reboot command")
        await self.simple_action_executor(self.drone.action.reboot, "reboot")

    @async_try_except(reraise=True)
    async def set_takeoff(self, takeoff_alt: float, **kwargs) -> None:
        """
        Commands the drone to takeoff to the given altitude.
        Will arm the drone if it is not already.
        """
        logger.info(f"Setting takeoff altitude to {takeoff_alt}")
        await self.drone.action.set_takeoff_altitude(takeoff_alt)
        await self.set_arm()
        logger.info("Sending takeoff command")
        await self.simple_action_executor(self.drone.action.takeoff, "takeoff")

    @async_try_except(reraise=True)
    async def upload_mission(self, waypoints: List[dict], **kwargs) -> None:
        """
        Calls the mission api to upload a mission to the fcc.
        """
        logger.info("Starting mission upload process")
        await self.mission_api.build_and_upload(waypoints)

    @async_try_except(reraise=True)
    async def begin_mission(self, **kwargs) -> None:
        """
        Arms the drone and calls the mission api to start a mission.
        """
        logger.info("Arming the drone")
        await self.set_arm()
        # we shouldn't have to check the armed status because
        # the arm fn should raise an exception if it is unsuccessful
        logger.info("Starting the mission")
        await self.mission_api.start()
        if self.in_air:
            self._publish_event("mission_starting_from_air_event")

    @async_try_except(reraise=True)
    async def pause_mission(self, **kwargs) -> None:
        """
        Calls the mission api to pasue a mission to the fcc.
        """
        logger.info("Starting mission upload process")
        await self.mission_api.pause()

    @async_try_except(reraise=True)
    async def resume_mission(self, **kwargs) -> None:
        """
        Calls the mission api to pasue a mission to the fcc.
        """
        logger.info("Resuming Mission")
        await self.mission_api.resume()

    # endregion ###############################################################

    # region ##################### O F F B O A R D ############################

    async def offboard_tasks(self) -> asyncio.Future:
        """
        Gathers the offboard tasks
        """
        return asyncio.gather(self.offboard_ned(), self.offboard_body())

    async def offboard_start(self, **kwargs) -> None:
        """
        Starts offboard mode on the drone. Use with caution!
        """
        logger.info("Starting offboard mode")
        await self.drone.offboard.start()
        self.offboard_enabled = True

    async def offboard_stop(self, **kwargs) -> None:
        """
        Stops offboard mode on the drone.
        """
        logger.info("Stopping offboard mode")
        self.offboard_enabled = False
        await self.drone.offboard.stop()

    async def offboard_ned(self) -> None:
        """
        Feeds offboard NED data to the drone.
        """
        logger.debug(f"offboard_ned loop started")

        @async_try_except()
        async def process_offboard_ned(msg: dict) -> None:
            # if not currently in offboard mode, skip
            if not self.offboard_enabled:
                return

            north = msg["north"]  # TODO - type cast these maybe?
            east = msg["east"]
            down = msg["down"]
            yaw = msg["yaw"]
            await self.drone.offboard.set_velocity_ned(
                VelocityNedYaw(north, east, down, yaw)
            )

        await self.async_queue_action(
            self.offboard_ned_queue,
            process_offboard_ned,
            frequency=20,
        )

    async def offboard_body(self) -> None:
        """
        Feeds offboard body data to the drone.
        """
        logger.debug(f"offboard_body loop started")

        @async_try_except()
        async def process_offboard_body(
            msg: dict,
        ) -> None:
            # if not currently in offboard mode, skip
            if not self.offboard_enabled:
                return

            forward = msg["forward"]  # TODO - type casting?
            right = msg["right"]
            down = msg["down"]
            yaw = msg["yaw"]
            await self.drone.offboard.set_velocity_ned(
                VelocityBodyYawspeed(forward, right, down, yaw)
            )

        await self.async_queue_action(
            self.offboard_body_queue,
            process_offboard_body,
            frequency=20,
        )

    # endregion ###############################################################


class MissionAPI(MAVMQTTBase):
    def __init__(self, drone: mavsdk.System, client: MQTTClient) -> None:
        super().__init__(client, drone)

        # this is solely for type hinting
        self.drone: mavsdk.System

    @async_try_except(reraise=True)
    async def set_geofence(
        self, min_lat: float, min_lon: float, max_lat: float, max_lon: float
    ) -> None:
        """
        Creates and uploads an inclusive geofence given min/max lat/lon.
        """
        logger.info(
            f"Uploading geofence of ({min_lat}, {min_lon}), ({max_lat}, {max_lon})"
        )

        # need to create a rectangle, PX4 isn't quite smart enough
        # to recognize only two corners
        tl_point = Point(max_lat, min_lon)
        tr_point = Point(max_lat, max_lon)
        bl_point = Point(min_lat, min_lon)
        br_point = Point(min_lat, max_lon)

        fence = [
            Polygon(
                [tl_point, tr_point, bl_point, br_point], Polygon.FenceType.INCLUSION
            )
        ]
        await self.drone.geofence.upload_geofence(fence)

    @async_try_except(reraise=True)
    async def build(self, waypoints: List[dict]) -> List[MissionItem]:
        """
        Convert a list of waypoints (dict) to a list of MissionItems.
        """
        mission_items = []

        # if the first waypoint is not a takeoff waypoint, create one
        if waypoints[0]["type"] != "takeoff":
            # use the altitude of the first waypoint
            waypoints.insert(0, {"type": "takeoff", "alt": waypoints[0]["alt"]})

        # now, check if first waypoint has a lat/lon
        # and if not, add lat lon of current position
        waypoint_0 = waypoints[0]
        if "lat" not in waypoints[0] or "lon" not in waypoints[0]:
            # get the next update from the raw gps and use that
            # .position() only updates on new positions
            position = await self.drone.telemetry.raw_gps().__anext__()
            waypoint_0["lat"] = position.latitude_deg
            waypoint_0["lon"] = position.longitude_deg

        # convert the dicts into mission_raw.MissionItems
        for seq, waypoint in enumerate(waypoints):
            waypoint_type = waypoint["type"]

            # https://mavlink.io/en/messages/common.html#MISSION_ITEM_INT
            command = None
            param1 = None
            param2 = None
            param3 = None
            param4 = None

            if waypoint_type == "takeoff":
                # https://mavlink.io/en/messages/common.html#MAV_CMD_NAV_TAKEOFF
                command = mavutil.mavlink.MAV_CMD_NAV_TAKEOFF
                param1 = 0  # pitch
                param2 = float("nan")  # empty
                param3 = float("nan")  # empty
                param4 = float("nan")  # yaw angle. NaN uses current yaw heading mode

            elif waypoint_type == "goto":
                # https://mavlink.io/en/messages/common.html#MAV_CMD_NAV_WAYPOINT
                command = mavutil.mavlink.MAV_CMD_NAV_WAYPOINT
                param1 = 0  # hold time
                param2 = 0  # accepteance radius
                param3 = 0  # pass radius, 0 goes straight through
                param4 = float("nan")  # yaw angle. NaN uses current yaw heading mode

            elif waypoint_type == "land":
                # https://mavlink.io/en/messages/common.html#MAV_CMD_NAV_LAND
                command = mavutil.mavlink.MAV_CMD_NAV_LAND
                param1 = 0  # abort altitude, 0 uses system default
                # https://mavlink.io/en/messages/common.html#PRECISION_LAND_MODE
                # precision landing mode
                param2 = mavutil.mavlink.PRECISION_LAND_MODE_DISABLED
                param3 = float("nan")  # empty
                param4 = float("nan")  # yaw angle. NaN uses current yaw heading mode

            # https://mavlink.io/en/messages/common.html#MAV_FRAME
            frame = mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT
            current = int(seq == 0)  # boolean
            autocontinue = int(True)
            x = int(float(waypoint["lat"]) * 10000000)
            y = int(float(waypoint["lon"]) * 10000000)
            z = float(waypoint["alt"])
            # https://mavlink.io/en/messages/common.html#MAV_MISSION_TYPE
            mission_type = mavutil.mavlink.MAV_MISSION_TYPE_MISSION

            mission_items.append(
                MissionItem(
                    seq=seq,
                    frame=frame,
                    command=command,
                    current=current,
                    autocontinue=autocontinue,
                    param1=param1,
                    param2=param2,
                    param3=param3,
                    param4=param4,
                    x=x,
                    y=y,
                    z=z,
                    mission_type=mission_type,
                )
            )

        return mission_items

    @async_try_except(reraise=True)
    async def upload(self, mission_items: List[MissionItem]) -> None:
        """
        Upload a given list of MissionItems to the drone.
        """
        try:
            logger.info("Clearing existing mission on the drone")
            await self.drone.mission_raw.clear_mission()
            logger.info("Uploading mission items to drone")
            await self.drone.mission_raw.upload_mission(mission_items)
            self._publish_event("mission_upload_success_event")
        except MissionRawError as e:
            logger.warning(
                f"Mission upload failed because: {str(e._result.result_str)}"
            )
            self._publish_event(
                "mission_upload_failed_event", str(e._result.result_str)
            )

    @async_try_except(reraise=True)
    async def build_and_upload(self, waypoints: List[dict]) -> None:
        """
        Upload a list of waypoints (dict) to the done.
        """
        mission_plan = await self.build(waypoints)
        await self.upload(mission_plan)

    @async_try_except(reraise=True)
    async def download(self) -> List[MissionItem]:
        """
        Download the current mission from the drone as a list of MissionItems.
        """
        logger.info("Downloading mission plan from drone")
        return await self.download()

    @async_try_except(reraise=True)
    async def wait_for_finish(self) -> None:
        """
        Async blocking function that waits for the current mission to be finished.
        """
        # self.drone.mission.is_missiion_finished unfortunately does not work,
        # with the mission_raw.MissionItems we've uploaded

        # if called immediately after a mission has been started, will immediately
        # exit as the drone hasn't even started moving to the first waypoint yet
        # give it 5 seconds to get moving first.
        mission_progress = await self.drone.mission_raw.mission_progress().__anext__()
        if mission_progress.current == 0:
            await asyncio.sleep(5)

        async for mission_progress in self.drone.mission_raw.mission_progress():
            if mission_progress.current == 0:
                return

    @async_try_except(reraise=True)
    async def start(self) -> None:
        """
        Commands the drone to start the current mission.
        Drone must already be armed.
        Will raise an exception if the active mission violates a geofence.
        """
        logger.info("Sending start mission command")
        await self.drone.mission_raw.start_mission()

    @async_try_except(reraise=True)
    async def hold(self) -> None:
        """
        Commands the drone to hold the current mission.
        """
        logger.info("Sending pause mission command")
        await self.drone.mission_raw.pause_mission()

    @async_try_except(reraise=True)
    async def pause(self) -> None:
        """
        Commands the drone to pause the current mission.
        """
        logger.info("Sending pause mission command")
        await self.hold()

    @async_try_except(reraise=True)
    async def resume(self) -> None:
        """
        Commands the drone to resume the paused mission.
        """
        logger.info("Sending resume mission command")
        await self.start()


class PyMAVLinkAgent(MAVMQTTBase):
    def __init__(self, client: MQTTClient, mocap_queue: queue.Queue) -> None:
        super().__init__(client)
        self.mocap_queue = mocap_queue

    @async_try_except()
    async def run(self) -> None:
        """
        Set up a mavlink connection and kick off any tasks
        """
        loop = asyncio.get_event_loop()

        # create a mavlink udp instance
        self.master = mavutil.mavlink_connection(
            "udpin:0.0.0.0:14542", source_system=254, dialect="bell"
        )

        await loop.run_in_executor(None, self.wait_for_heartbeat)
        asyncio.gather(self.set_hil_gps())

        while True:
            await asyncio.sleep(3)

    def wait_for_heartbeat(self) -> Any:
        """
        Wait for a MAVLINK heartbeat message.
        """
        try:
            logger.debug("Waiting for mavlink heartbeat")
            m = self.master.recv_match(type="HEARTBEAT", blocking=True)
            logger.debug("C O N N E C T E D")
            return m
        except Exception as e:
            logger.exception("Issue while waiting for connection heartbeat")

    @async_try_except()
    async def set_hil_gps(self) -> None:
        """
        Sends GPS position / velocity / heading to PX4,
        used to fake a GPS signal while we fly indoors.

        This is not the standard hil_gps message in the mavlink common message set,
        this is a custom mavlink message that includes heading,
        because the standard message doesn't.
        """

        def print_stats(last_print_time: float) -> float:
            """
            Takes the last print time, and determines
            whether or not to print statistics. Returns
            the last time statistics were printed.
            """
            if time.time() - last_print_time > 1:
                #logger.debug(f"Number of mocap messages {num_mocaps}")
                self.mqtt_client.publish(
                f"{self.topic_prefix}/hil_gps/stats",
                json.dumps({"num_frames":num_mocaps}),
                retain=False,
                qos=0,
            )
                return time.time()
            return last_print_time

        def mocap_msg_to_offboard_msg(
            mocap_msg: dict,
        ) -> dict:
            """
            Function to convert the msg coming over the wire to the hil msg
            needed for the hil_gps message
            """
            hilgps = {}

            hilgps["time_usec"] = int(mocap_msg["time_usec"])  # microseconds
            hilgps["fix_type"] = int(mocap_msg["fix_type"])
            hilgps["lat"] = int(mocap_msg["lat"])
            hilgps["lon"] = int(mocap_msg["lon"])
            hilgps["alt"] = int(mocap_msg["alt"])  
            hilgps["eph"] = int(mocap_msg["eph"])  # horizontal dilution of precision in ?
            hilgps["epv"] = int(mocap_msg["epv"])  # vertical duilution of precision in ?
            hilgps["vel"] = int(mocap_msg["vel"] )
            hilgps["v_north"] = int(mocap_msg["vn"])
            hilgps["v_east"] = int(mocap_msg["ve"])
            hilgps["v_down"] = int(mocap_msg["vd"])
            hilgps["cog"] = int(mocap_msg["cog"])
            hilgps["sats_visible"] = int(mocap_msg["satellites_visible"])
            hilgps["heading"] = int(mocap_msg["heading"])

            return hilgps

        def send_hil_gps(gps_data: dict) -> None:
            """
            Sends the HIL GPS message.
            """
            try:
                msg = self.master.mav.hil_gps_heading_encode(  # type: ignore
                    gps_data["time_usec"],
                    gps_data["fix_type"],
                    gps_data["lat"],
                    gps_data["lon"],
                    gps_data["alt"],
                    gps_data["eph"],
                    gps_data["epv"],
                    gps_data["vel"],
                    gps_data["v_north"],
                    gps_data["v_east"],
                    gps_data["v_down"],
                    gps_data["cog"],
                    gps_data["sats_visible"],
                    gps_data["heading"],
                )
                self.master.mav.send(msg)  # type: ignore
            except Exception as e:
                logger.exception("Issue send HIL GPS")

        HIL_FREQ = 15

        last_print_time = time.time()
        last_send_time = time.time()

        num_mocaps = 0

        while True:
            try:
                # print statistics
                last_print_time = print_stats(last_print_time)
                # get the next item
                data = self.mocap_queue.get_nowait()

                msg = data["hil_gps"]

                num_mocaps += 1
                now = time.time()

                # if time to send a new item, do so
                if now - last_send_time > (1 / HIL_FREQ):
                    # prepare hil data
                    hil_data = mocap_msg_to_offboard_msg(msg)
                    # send it
                    send_hil_gps(hil_data)
                    last_send_time = time.time()
            except queue.Empty:
                await asyncio.sleep(0.01)
                continue
            except Exception as e:
                logger.exception("Issue sending HIL GPS")
                continue
