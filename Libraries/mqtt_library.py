from __future__ import annotations

import copy
import json
from re import X
from typing import (
    Any,
    Dict,
    List,
    Literal,
    Optional,
    Protocol,
    Tuple,
    TypedDict,
    overload,
)

import paho.mqtt.client as mqtt
from loguru import logger


class VRCAutonomousMessage(TypedDict):
    enable: bool


class VRCPcmSetBaseColorMessage(TypedDict):
    wrgb: Tuple[int, int, int, int]


class VRCPcmSetTempColorMessage(TypedDict):
    wrgb: Tuple[int, int, int, int]
    time: float


class VRCPcmSetLaserOn(TypedDict):
    pass


class VRCPcmSetLaserOff(TypedDict):
    pass


class VRCPcmSetServoOpenCloseMessage(TypedDict):
    servo: int
    action: Literal["open", "close"]


class VRCPcmSetServoMinMessage(TypedDict):
    servo: int
    min_pulse: int


class VRCPcmSetServoMaxMessage(TypedDict):
    servo: int
    max_pulse: int


class VRCPcmSetServoPctMessage(TypedDict):
    servo: int
    percent: int


class VRCPcmResetMessage(TypedDict):
    pass


class VRCFusionPositionNedMessage(TypedDict):
    n: float
    e: float
    d: float


class VRCFusionVelocityNedMessage(TypedDict):
    Vn: float
    Ve: float
    Vd: float


class VRCFusionGeodetic(TypedDict):
    lat: float
    lon: float
    alt: float


class VRCFcmHilGpsStatsMessage(TypedDict):
    num_frames: int


class VRCFusionGeoMessage(TypedDict):
    geodetic: VRCFusionGeodetic


class VRCFusionGroundspeedMessage(TypedDict):
    groundspeed: float


class VRCFusionCourseMessage(TypedDict):
    course: float


class VRCFusionClimbrateMessage(TypedDict):
    climb_rate_fps: float


class VRCFusionAttitudeQuatMessage(TypedDict):
    w: float
    x: float
    y: float
    z: float


class VRCFusionAttitudeEulerMessage(TypedDict):
    psi: float
    theta: float
    phi: float


class VRCFusionAttitudeHeadingMessage(TypedDict):
    heading: float


class VRCFusionHilGpsMessage(TypedDict):
    time_usec: int
    fix_type: int
    lat: int
    lon: int
    alt: int
    eph: int
    epv: int
    vel: int
    vn: int
    ve: int
    vd: int
    cog: int
    satellites_visible: int
    heading: int


class VRCVioResyncMessage(TypedDict):
    n: float
    e: float
    d: float
    heading: float


class VRCVioPositionNedMessage(TypedDict):
    n: float
    e: float
    d: float


class VRCVioVelocityNedMessage(TypedDict):
    n: float
    e: float
    d: float


class VRCVioOrientationEulMessage(TypedDict):
    psi: float
    theta: float
    phi: float


class VRCVioOrientationQuatMessage(TypedDict):
    w: float
    x: float
    y: float
    z: float


class VRCVioHeadingMessage(TypedDict):
    degrees: float


class VRCVioConfidenceMessage(TypedDict):
    mapper: float
    tracker: float


class VRCApriltagsSelectedPos(TypedDict):
    n: float
    e: float
    d: float


class VRCApriltagsSelectedMessage(TypedDict):
    tag_id: int
    pos: VRCApriltagsSelectedPos
    heading: float


class VRCApriltagsVisibleTagsPosRel(TypedDict):
    x: float
    y: float
    z: float


class VRCApriltagsVisibleTagsPosWorld(TypedDict):
    x: Optional[float]
    y: Optional[float]
    z: Optional[float]


class VRCApriltagsVisibleTagsMessage(TypedDict):
    id: int
    horizontal_dist: float
    vertical_dist: float
    angle_to_tag: float
    heading: float
    pos_rel: VRCApriltagsVisibleTagsPosRel
    pos_world: VRCApriltagsVisibleTagsPosWorld


class VRCApriltagsRawPos(TypedDict):
    x: float
    y: float
    z: float


class VRCApriltagsRawMessage(TypedDict):
    id: int
    pos: VRCApriltagsRawPos
    rotation: Tuple[
        Tuple[float, float, float],
        Tuple[float, float, float],
        Tuple[float, float, float],
    ]


class VRCFcmEventsMessage(TypedDict):
    name: str
    payload: dict
    timestamp: str


class VRCFcmBatteryMessage(TypedDict):
    voltage: float
    soc: float
    timestamp: str


class VRCFcmStatusMessage(TypedDict):
    armed: bool
    mode: str
    timestamp: str


class VRCFcmLocationLocalMessage(TypedDict):
    dX: float
    dY: float
    dZ: float
    timestamp: str


class VRCFcmLocationGlobalMessage(TypedDict):
    lat: float
    lon: float
    alt: float
    hdg: float
    timestamp: str


class VRCFcmLocationHomeMessage(TypedDict):
    lat: float
    lon: float
    alt: float
    timestamp: str


class VRCFcmAttitudeEulerMessage(TypedDict):
    roll: float
    pitch: float
    yaw: float
    timestamp: str


class VRCFcmVelocityMessage(TypedDict):
    vX: float
    vY: float
    vZ: float
    timestamp: str


class MQTTMessageCache:
    def __init__(self) -> None:
        self.__storage = {}

    # fmt: off
    @overload
    def __getitem__(self, key: Literal["vrc/autonomous"]) -> VRCAutonomousMessage: ...

    @overload
    def __getitem__(self, key: Literal["vrc/pcm/set_base_color"]) -> VRCPcmSetBaseColorMessage: ...

    @overload
    def __getitem__(self, key: Literal["vrc/pcm/set_temp_color"]) -> VRCPcmSetTempColorMessage: ...

    @overload
    def __getitem__(self, key: Literal["vrc/pcm/set_servo_open_close"]) -> VRCPcmSetServoOpenCloseMessage: ...

    @overload
    def __getitem__(self, key: Literal["vrc/pcm/set_laser_on"]) -> VRCPcmSetLaserOnMessage: ...

    @overload
    def __getitem__(self, key: Literal["vrc/pcm/set_laser_off"]) -> VRCPcmSetLaserOffMessage: ...

    @overload
    def __getitem__(self, key: Literal["vrc/pcm/set_servo_min"]) -> VRCPcmSetServoMinMessage: ...

    @overload
    def __getitem__(self, key: Literal["vrc/pcm/set_servo_max"]) -> VRCPcmSetServoMaxMessage: ...

    @overload
    def __getitem__(self, key: Literal["vrc/pcm/set_servo_pct"]) -> VRCPcmSetServoPctMessage: ...

    @overload
    def __getitem__(self, key: Literal["vrc/pcm/reset"]) -> VRCPcmResetMessage: ...

    @overload
    def __getitem__(self, key: Literal["vrc/fusion/position/ned"]) -> VRCFusionPositionNedMessage: ...

    @overload
    def __getitem__(self, key: Literal["vrc/fusion/geo"]) -> VRCFusionGeoMessage: ...

    @overload
    def __getitem__(self, key: Literal["vrc/fusion/groundspeed"]) -> VRCFusionGroundspeedMessage: ...

    @overload
    def __getitem__(self, key: Literal["vrc/fusion/velocity/ned"]) -> VRCFusionVelocityNedMessage: ...

    @overload
    def __getitem__(self, key: Literal["vrc/fusion/course"]) -> VRCFusionCourseMessage: ...

    @overload
    def __getitem__(self, key: Literal["vrc/fusion/climbrate"]) -> VRCFusionClimbrateMessage: ...

    @overload
    def __getitem__(self, key: Literal["vrc/fusion/attitude/quat"]) -> VRCFusionAttitudeQuatMessage: ...

    @overload
    def __getitem__(self, key: Literal["vrc/fusion/attitude/euler"]) -> VRCFusionAttitudeEulerMessage: ...

    @overload
    def __getitem__(self, key: Literal["vrc/fusion/attitude/heading"]) -> VRCFusionAttitudeHeadingMessage: ...

    @overload
    def __getitem__(self, key: Literal["vrc/fusion/hil_gps"]) -> VRCFusionHilGpsMessage: ...

    @overload
    def __getitem__(self, key: Literal["vrc/vio/resync"]) -> VRCVioResyncMessage: ...

    @overload
    def __getitem__(self, key: Literal["vrc/vio/position/ned"]) -> VRCVioPositionNedMessage: ...

    @overload
    def __getitem__(self, key: Literal["vrc/vio/velocity/ned"]) -> VRCVioVelocityNedMessage: ...

    @overload
    def __getitem__(self, key: Literal["vrc/vio/orientation/eul"]) -> VRCVioOrientationEulMessage: ...

    @overload
    def __getitem__(self, key: Literal["vrc/vio/orientation/quat"]) -> VRCVioOrientationQuatMessage: ...

    @overload
    def __getitem__(self, key: Literal["vrc/vio/heading"]) -> VRCVioHeadingMessage: ...

    @overload
    def __getitem__(self, key: Literal["vrc/vio/confidence"]) -> VRCVioConfidenceMessage: ...

    @overload
    def __getitem__(self, key: Literal["vrc/apriltags/selected"]) -> VRCApriltagsSelectedMessage: ...

    @overload
    def __getitem__(self, key: Literal["vrc/apriltags/raw"]) -> List[VRCApriltagsRawMessage]: ...

    @overload
    def __getitem__(self, key: Literal["vrc/apriltags/visible_tags"]) -> List[VRCApriltagsVisibleTagsMessage]: ...

    @overload
    def __getitem__(self, key: Literal["vrc/apriltags/fps"]) -> int: ...

    @overload
    def __getitem__(self, key: Literal["vrc/fcm/events"]) -> VRCFcmEventsMessage: ...

    @overload
    def __getitem__(self, key: Literal["vrc/fcm/battery"]) -> VRCFcmBatteryMessage: ...

    @overload
    def __getitem__(self, key: Literal["vrc/fcm/status"]) -> VRCFcmStatusMessage: ...

    @overload
    def __getitem__(self, key: Literal["vrc/fcm/location/local"]) -> VRCFcmLocationLocalMessage: ...

    @overload
    def __getitem__(self, key: Literal["vrc/fcm/location/global"]) -> VRCFcmLocationGlobalMessage: ...

    @overload
    def __getitem__(self, key: Literal["vrc/fcm/location/home"]) -> VRCFcmLocationHomeMessage: ...

    @overload
    def __getitem__(self, key: Literal["vrc/fcm/attitude/euler"]) -> VRCFcmAttitudeEulerMessage: ...

    @overload
    def __getitem__(self, key: Literal["vrc/fcm/velocity"]) -> VRCFcmVelocityMessage: ...
    # fmt: on

    def __getitem__(self, key: str) -> Any:
        if key in self.__storage:
            return self.__storage[key]
        else:
            return None

    def __setitem__(self, key: str, value: Any) -> None:
        self.__storage[key] = value

    def __contains__(self, key: str) -> bool:
        return key in self.__storage


class MQTTCallable(Protocol):
    def __call__(self, payload: Any) -> Any:
        ...


class MQTTModule:
    """
    Generic MQTT Module class that should be inherited by other modules.
    `topic_prefix` should be a lowercase string that is the namespace
    for the class's MQTT messages. Additionally, the `topic_map` should
    be a dictionary of topics to functions that will be called with a dictionary
    payload.
    """

    def __init__(self, host="mqtt"):
        # these should be not be changed, to match the docker-compose.yml file
        self.mqtt_host = host
        self.mqtt_port = 18830

        # create the MQTT client
        self.mqtt_client = mqtt.Client()

        # set up the on connect and on message handlers
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message

        # dictionary of MQTT topics to callback functions
        # this is intended to be overwritten by the child class
        self.topic_map: Dict[str, MQTTCallable] = {}

        # maintain a cache of the last message sent on a topic by this module
        self.message_cache = MQTTMessageCache()

    def run(self) -> None:
        """
        Class entrypoint. Connects to the MQTT broker and starts the MQTT loop
        in a blocking manner.
        """
        # connect the MQTT client
        self.mqtt_client.connect(host=self.mqtt_host, port=self.mqtt_port, keepalive=60)
        # run forever
        self.mqtt_client.loop_forever()

    def run_non_blocking(self) -> None:
        """
        Class entrypoint. Connects to the MQTT broker and starts the MQTT loop
        in a non-blocking manner.
        """
        # connect the MQTT client
        self.mqtt_client.connect(host=self.mqtt_host, port=self.mqtt_port, keepalive=60)
        # run in background
        self.mqtt_client.loop_start()

    def on_message(
        self, client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage
    ) -> None:
        """
        On message callback, Dispatches the message to the appropriate function.
        """
        try:
            # logger.debug(f"Recieved {msg.topic}: {msg.payload}")
            if msg.topic in self.topic_map:
                # we talk JSON, no exceptions
                payload = json.loads(msg.payload)
                self.topic_map[msg.topic](payload)

        except Exception as e:
            logger.exception(f"Error handling message on {msg.topic}")

    def on_connect(
        self,
        client: mqtt.Client,
        userdata: Any,
        rc: Any,
        properties: Optional[mqtt.Properties] = None,
    ) -> None:
        """
        On connection callback. Subscribes to MQTT topics in the topic map.
        """
        logger.debug(f"Connected with result code {rc}")

        for topic in self.topic_map.keys():
            client.subscribe(topic)
            logger.success(f"Subscribed to: {topic}")

    # fmt: off
    @overload
    def send_message(self, topic: Literal["vrc/autonmous"], payload: VRCAutonomousMessage) -> None: ...

    @overload
    def send_message(self, topic: Literal["vrc/pcm/set_base_color"], payload: VRCPcmSetBaseColorMessage) -> None: ...

    @overload
    def send_message(self, topic: Literal["vrc/pcm/set_temp_color"], payload: VRCPcmSetTempColorMessage) -> None: ...

    @overload
    def send_message(self, topic: Literal["vrc/pcm/set_servo_open_close"], payload: VRCPcmSetServoOpenCloseMessage) -> None: ...

    @overload
    def send_message(self, topic: Literal["vrc/pcm/set_laser_on"], payload: VRCPcmSetLaserOnMessage) -> None: ...

    @overload
    def send_message(self, topic: Literal["vrc/pcm/set_laseer_off"], payload: VRCPcmSetLaserOffMessage) -> None: ...

    @overload
    def send_message(self, topic: Literal["vrc/pcm/set_servo_min"], payload: VRCPcmSetServoMinMessage) -> None: ...

    @overload
    def send_message(self, topic: Literal["vrc/pcm/set_servo_max"], payload: VRCPcmSetServoMaxMessage) -> None: ...

    @overload
    def send_message(self, topic: Literal["vrc/pcm/set_servo_pct"], payload: VRCPcmSetServoPctMessage) -> None: ...

    @overload
    def send_message(self, topic: Literal["vrc/pcm/reset"], payload: VRCPcmResetMessage) -> None: ...

    @overload
    def send_message(self, topic: Literal["vrc/fusion/position/ned"], payload: VRCFusionPositionNedMessage) -> None: ...

    @overload
    def send_message(self, topic: Literal["vrc/fusion/geo"], payload: VRCFusionGeoMessage) -> None: ...

    @overload
    def send_message(self, topic: Literal["vrc/fusion/groundspeed"], payload: VRCFusionGroundspeedMessage) -> None: ...

    @overload
    def send_message(self, topic: Literal["vrc/fusion/velocity/ned"], payload: VRCFusionVelocityNedMessage) -> None: ...

    @overload
    def send_message(self, topic: Literal["vrc/fusion/course"], payload: VRCFusionCourseMessage) -> None: ...

    @overload
    def send_message(self, topic: Literal["vrc/fusion/climbrate"], payload: VRCFusionClimbrateMessage) -> None: ...

    @overload
    def send_message(self, topic: Literal["vrc/fusion/attitude/quat"], payload: VRCFusionAttitudeQuatMessage) -> None: ...

    @overload
    def send_message(self, topic: Literal["vrc/fusion/attitude/euler"], payload: VRCFusionAttitudeEulerMessage) -> None: ...

    @overload
    def send_message(self, topic: Literal["vrc/fusion/attitude/heading"], payload: VRCFusionAttitudeHeadingMessage) -> None: ...

    @overload
    def send_message(self, topic: Literal["vrc/fusion/hil_gps"], payload: VRCFusionHilGpsMessage) -> None: ...

    @overload
    def send_message(self, topic: Literal["vrc/vio/resync"], payload: VRCVioResyncMessage) -> None: ...

    @overload
    def send_message(self, topic: Literal["vrc/vio/position/ned"], payload: VRCVioPositionNedMessage) -> None: ...

    @overload
    def send_message(self, topic: Literal["vrc/vio/velocity/ned"], payload: VRCVioVelocityNedMessage) -> None: ...

    @overload
    def send_message(self, topic: Literal["vrc/vio/orientation/eul"], payload: VRCVioOrientationEulMessage) -> None: ...

    @overload
    def send_message(self, topic: Literal["vrc/vio/orientation/quat"], payload: VRCVioOrientationQuatMessage) -> None: ...

    @overload
    def send_message(self, topic: Literal["vrc/vio/heading"], payload: VRCVioHeadingMessage) -> None: ...

    @overload
    def send_message(self, topic: Literal["vrc/vio/confidence"], payload: VRCVioConfidenceMessage) -> None: ...

    @overload
    def send_message(self, topic: Literal["vrc/apriltags/selected"], payload: VRCApriltagsSelectedMessage) -> None: ...

    @overload
    def send_message(self, topic: Literal["vrc/apriltags/raw"], payload: List[VRCApriltagsRawMessage]) -> None: ...

    @overload
    def send_message(self, topic: Literal["vrc/apriltags/visible_tags"], payload: List[VRCApriltagsVisibleTagsMessage]) -> None: ...

    @overload
    def send_message(self, topic: Literal["vrc/apriltags/fps"], payload: int) -> None: ...

    @overload
    def send_message(self, topic: Literal["vrc/fcm/events"], payload: VRCFcmEventsMessage) -> None: ...

    @overload
    def send_message(self, topic: Literal["vrc/fcm/battery"], payload: VRCFcmBatteryMessage) -> None: ...

    @overload
    def send_message(self, topic: Literal["vrc/fcm/status"], payload: VRCFcmStatusMessage) -> None: ...

    @overload
    def send_message(self, topic: Literal["vrc/fcm/location/local"], payload: VRCFcmLocationLocalMessage) -> None: ...

    @overload
    def send_message(self, topic: Literal["vrc/fcm/location/global"], payload: VRCFcmLocationGlobalMessage) -> None: ...

    @overload
    def send_message(self, topic: Literal["vrc/fcm/location/home"], payload: VRCFcmLocationHomeMessage) -> None: ...

    @overload
    def send_message(self, topic: Literal["vrc/fcm/attitude/euler"], payload: VRCFcmAttitudeEulerMessage) -> None: ...

    @overload
    def send_message(self, topic: Literal["vrc/fcm/velocity"], payload: VRCFcmVelocityMessage) -> None: ...

    # fmt: on
    def send_message(self, topic: str, payload: Any) -> None:
        """
        Sends a message to the MQTT broker.
        """
        # logger.debug(f"Sending message to {topic}: {payload}")
        self.mqtt_client.publish(topic, json.dumps(payload))
        self.message_cache[topic] = copy.deepcopy(payload)
