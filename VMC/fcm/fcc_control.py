import asyncio
import contextlib
import json
import math
import queue
import time
from typing import Any, Callable, List

import mavsdk
from mavsdk.geofence import Point, Polygon
from mavsdk.mission_raw import MissionItem, MissionRawError
from pymavlink import mavutil

from bell.avr.mqtt.client import MQTTModule
from bell.avr.mqtt.payloads import AvrFcmEventsPayload
from bell.avr.utils.decorators import async_try_except, try_except
from bell.avr.utils.timing import rate_limit
from loguru import logger
from mavsdk.action import ActionError
from fcc_mqtt import FCMMQTTModule
import sys


class DispatcherBusy(Exception):
    """
    Exception for when the action dispatcher is currently busy
    executing another action
    """


class DispatcherManager(FCMMQTTModule):
    def __init__(self) -> None:
        super().__init__()
        self.currently_running_task = None
        self.timeout = 10

    async def schedule_task(self, task: Callable, payload: Any, name: str) -> None:
        """
        Schedule a task (async func) to be run by the dispatcher with the
        given payload. Task name is also required for printing.
        """
        logger.debug(f"Scheduling a task for '{name}'")
        # if the dispatcher is ok to take on a new task
        if (
            self.currently_running_task is not None
            and self.currently_running_task.done()
        ) or self.currently_running_task is None:
            await self.create_task(task, payload, name)
        else:
            raise DispatcherBusy

    async def create_task(self, task: Callable, payload: dict, name: str) -> None:
        """
        Create a task to be run.
        """
        self.currently_running_task = asyncio.create_task(
            self.task_waiter(task, payload, name)
        )

    async def task_waiter(self, task: Callable, payload: dict, name: str) -> None:
        """
        Execute a task with a timeout.
        """
        try:
            await asyncio.wait_for(task(**payload), timeout=self.timeout)
            self._publish_event(f"request_{name}_completed_event")
            self.currently_running_task = None

        except asyncio.TimeoutError:
            try:
                logger.warning(f"Task '{name}' timed out!")
                self._publish_event("action_timeout_event", name)
                self.currently_running_task = None

            except Exception:
                logger.exception("ERROR IN TIMEOUT HANDLER")

        except Exception:
            logger.exception("ERROR IN TASK WAITER")


class ControlManager(FCMMQTTModule):
    def __init__(self) -> None:
        super().__init__()

        # mavlink stuff
        self.drone = mavsdk.System(sysid=141)

        # queues
        self.action_queue = queue.Queue()

        self.topic_map = {"avr/fcm/actions": self.handle_action_message}

    async def connect(self) -> None:
        """
        Connect the Drone object.
        """
        logger.debug("Control: Connecting to the FCC")

        # mavsdk does not support dns
        await self.drone.connect(system_address="tcp://127.0.0.1:5761")

        logger.success("Connected to the FCC")

    async def run_non_blocking(self) -> asyncio.Future:
        """
        Run the Flight Control Computer module
        """
        # start our MQTT client
        super().run_non_blocking()

        # connect to the fcc
        await self.connect()

        # start the mission api MQTT client
        # self.mission_api.run_non_blocking()

        # start tasks
        return asyncio.gather(
            # uncomment the following lines to enable outside control
            self.action_dispatcher(),
        )

    async def run(self) -> asyncio.Future:
        asyncio.gather(self.run_non_blocking())
        while True:
            await asyncio.sleep(1)

    # region ################## D I S P A T C H E R  ##########################

    def handle_action_message(self, payload):
        self.action_queue.put(payload)

    @async_try_except()
    async def action_dispatcher(self) -> None:
        logger.debug("action_dispatcher started")

        action_map = {
            "break": self.set_intentional_timeout,
            "connect": self.connect,
            "arm": self.set_arm,
            "disarm": self.set_disarm,
            "kill": self.set_kill,
            "land": self.set_land,
            "reboot": self.set_reboot,
            "takeoff": self.set_takeoff,
            "goto_location": self.goto_location,
            "upload_mission": self.build_and_upload,
            "start_mission": self.start_mission,
        }

        dispatcher = DispatcherManager()
        dispatcher.run_non_blocking()

        while True:
            action = {}
            try:
                action = self.action_queue.get_nowait()

                if action["payload"] == "":
                    action["payload"] = "{}"

                if action["action"] in action_map:
                    # payload = json.loads(action["payload"])
                    payload = action["payload"]
                    await dispatcher.schedule_task(
                        action_map[action["action"]], payload, action["action"]
                    )
                else:
                    logger.warning(f"Unknown action: {action['name']}")

            except DispatcherBusy:
                logger.info("I'm busy running another task, try again later")
                self._publish_event("fcc_busy_event", payload=action["action"])

            except queue.Empty:
                await asyncio.sleep(0.1)

            except Exception:
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
            full_success_str = f"{action_text}_success_event"
            logger.info(f"Sending {full_success_str}")
            self._publish_event(full_success_str)

        except ActionError as e:
            full_fail_str = f"{action_text}_failed_event"
            logger.info(f"Sending {full_fail_str}")
            self._publish_event(full_fail_str)

            if e._result.result_str == "CONNECTION_ERROR":
                asyncio.create_task(self.connect())

            raise e from e

    # endregion ###############################################################

    # region #####################  A C T I O N S #############################

    @async_try_except()
    async def set_intentional_timeout(self, **kwargs) -> None:
        """
        Sets a 20 second timeout.
        """
        with contextlib.suppress(asyncio.CancelledError):
            await asyncio.sleep(20)

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
    async def set_takeoff(self, **kwargs) -> None:
        """
        Commands the drone to takeoff to the given altitude.
        Will arm the drone if it is not already.
        """
        alt = kwargs["alt"]
        logger.info(f"Setting takeoff altitude to {alt}")
        await self.drone.action.set_takeoff_altitude(alt)
        await self.set_arm()
        logger.info("Sending takeoff command")
        await self.simple_action_executor(self.drone.action.takeoff, "takeoff")

    @async_try_except(reraise=True)
    async def goto_location(self, **kwargs) -> None:
        """
        Commands the drone to go to a location.
        """
        logger.warning("Sending go to location")
        await self.drone.action.goto_location(
            kwargs["lat"], kwargs["lon"], kwargs["alt"], kwargs["heading"]
        )

    @async_try_except(reraise=True)
    async def build(self, waypoints: List[dict]) -> List[MissionItem]:
        # sourcery skip: hoist-statement-from-loop, switch, use-assigned-variable
        """
        Convert a list of waypoints (dict) to a list of MissionItems.
        """
        mission_items = []

        # # if the first waypoint is not a takeoff waypoint, create one
        # if waypoints[0]["type"] != "takeoff":
        #     # use the altitude of the first waypoint
        #     waypoints.insert(0, {"type": "takeoff", "alt": waypoints[0]["alt"]})

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
            logger.info("Mission Upload SUCESS")
        except MissionRawError as e:
            logger.warning(f"Mission upload failed because: {e._result.result_str}")
            self._publish_event(
                "mission_upload_failed_event", str(e._result.result_str)
            )

    @async_try_except(reraise=True)
    async def build_and_upload(self, **kwargs) -> None:
        """
        Upload a list of waypoints (dict) to the done.
        """
        mission_plan = await self.build(kwargs["waypoints"])
        await self.upload(mission_plan)

    @async_try_except(reraise=True)
    async def start_mission(self) -> None:
        """
        Commands the drone to start the current mission.
        Drone must already be armed.
        Will raise an exception if the active mission violates a geofence.
        """
        logger.info("Sending start mission command")
        await self.drone.mission_raw.start_mission()

    @async_try_except(reraise=True)
    async def set_geofence(self, **kwargs) -> None:
        """
        Creates and uploads an inclusive geofence given min/max lat/lon.
        """

        min_lat = kwargs["min_lat"]
        min_lon = kwargs["min_lon"]
        max_lat = kwargs["max_lat"]
        max_lon = kwargs["max_lon"]

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

    # endregion ###############################################################


if __name__ == "__main__":
    control = ControlManager()
    asyncio.run(control.run())
