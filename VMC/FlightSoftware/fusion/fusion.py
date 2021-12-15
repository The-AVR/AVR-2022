import json
import threading
import time
from math import atan2, pi
from typing import Any

import numpy as np
import paho.mqtt.client as mqtt
import pymap3d
from loguru import logger


class Fusion:
    def __init__(self):
        self.config = {
            "origin": {"lat": 32.807650, "lon": -97.157153, "alt": 161.5},
            "hil_gps_constants": {
                "fix_type": 3,
                "eph": 20,
                "epv": 5,
                "satellites_visible": 13,
            },
            "COURSE_THRESHOLD": 10,
            "POS_DETLA_THRESHOLD": 10,
            "POS_D_THRESHOLD": 30,
            "HEADING_DELTA_THRESHOLD": 5,
            "AT_THRESH": 0.25,
            "T265_THRESH": 0.25,
            "AT_DERIV_THRESH": 10,
            "INIT_WAIT_TIME": 2,
        }

        self.mqtt_host = "mqtt"
        self.mqtt_port = 18830

        self.mqtt_client = mqtt.Client()

        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message

        self.topic_prefix = "vrc/fusion"

        self.topic_map = {
            "vrc/vio/position/ned": self.fuse_pos,
            "vrc/vio/orientation/eul": self.fuse_att_euler,
            "vrc/vio/heading": self.fuse_att_heading,
            "vrc/vio/velocity/ned": self.fuse_vel,
            f"{self.topic_prefix}/pos/ned": self.local_to_geo,
            # "vrc/apriltags/selected/pos": self.on_apriltag_message
        }

        self.primary_topic = None
        self.norm = None
        self.heading_delta = None
        self.deriv_norm = None

        self.local_copy = {}

        self.vio_init = False
        self.at_init = False

        # on_apriltag storage
        self.last_pos = [0, 0, 0]
        self.deriv = [0, 0, 0]
        self.last_apriltag = time.time()

        logger.success("FUS: Object created!")

    def on_message(
        self, client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage
    ) -> None:
        try:
            # logger.debug(f"{msg.topic}: {str(msg.payload)}")
            if msg.topic in self.topic_map:
                payload = json.loads(msg.payload)
                self.topic_map[msg.topic](payload)
        except Exception as e:
            logger.exception(f"Error handling message on {msg.topic}")

    def on_connect(
        self,
        client: mqtt.Client,
        userdata: Any,
        rc: int,
        properties: mqtt.Properties = None,
    ) -> None:
        logger.debug(f"FUS: Connected with result code {rc}")
        for topic in self.topic_map.keys():
            logger.debug(f"FUS: Subscribed to: {topic}")
            client.subscribe(topic)

    def local_to_geo(self, msg: dict) -> None:
        """
        Callback for the fusion/pos topic. This method calculates the
        geodetic location from an NED position and origin and publishes it.
        """
        origin = [
            self.config["origin"]["lat"],
            self.config["origin"]["lon"],
            self.config["origin"]["alt"],
        ]

        try:
            ned = msg
            lla = pymap3d.enu2geodetic(
                float(ned["e"]) / 100,  # type: ignore # East   | Y
                float(ned["n"]) / 100,  # type: ignore # North  | X
                -1 * float(ned["d"]) / 100,  # type: ignore # Up     | Z
                origin[0],  # Origin lat
                origin[1],  # Origin lon
                origin[2],  # Origin alt
                deg=True,
            )

            geo_update = {"geodetic": {"lat": lla[0], "lon": lla[1], "alt": lla[2]}}
            self.mqtt_client.publish(
                f"{self.topic_prefix}/geo",
                json.dumps(geo_update),
                retain=False,
                qos=0,
            )

            self.local_copy["geo"] = dict(geo_update["geodetic"])

        except Exception as e:
            logger.exception("FUS: Error updating Geodetic location")
            raise e

    def fuse_pos(self, msg: dict) -> None:
        """
        Callback for receiving pos data in NED reference frame from vio and publishes into a fusion/pos topic.

        VRC doesnt have sophisticated fusion yet, so this just re-routes the message onto the fusion topic.

        """
        try:
            pos_update = {"n": msg["n"], "e": msg["e"], "d": msg["d"]}

            self.mqtt_client.publish(
                f"{self.topic_prefix}/pos/ned",
                json.dumps(pos_update),
                retain=False,
                qos=0,
            )

            self.local_copy["pos"] = dict(pos_update)

        except Exception as e:
            logger.exception("FUS: Error fusing pos sources")
            raise e

    def fuse_vel(self, msg: dict) -> None:
        """
        Callback for receiving vel data in NED reference frame from vio and publishes into a fusion/vel topic.

        VRC doesnt have sophisticated fusion yet, so this just re-routes the message onto the fusion topic.

        """
        try:

            self.vio_init = True

            vmc_vel_update = {"Vn": msg["n"], "Ve": msg["e"], "Vd": msg["d"]}

            self.mqtt_client.publish(
                f"{self.topic_prefix}/vel/ned",
                json.dumps(vmc_vel_update),
                retain=False,
                qos=0,
            )

            self.local_copy["vel"] = dict(vmc_vel_update)

            # compute groundspeed
            gs = np.linalg.norm([msg["n"], msg["e"]])
            groundspeed_update = {"groundspeed": gs}

            self.mqtt_client.publish(
                f"{self.topic_prefix}/vel/groundspeed",
                json.dumps(groundspeed_update),
                retain=False,
                qos=0,
            )

            self.local_copy["groundspeed"] = dict(groundspeed_update)

            # arctan gets real noisy when the values get small, so we just lock course
            # to heading when we aren't really moving
            if gs >= self.config["COURSE_THRESHOLD"]:
                course = atan2(msg["e"], msg["n"])
                # wrap [-pi, pi] to [0, 360]
                if course < 0:
                    course += 2 * pi
                # rad to deg
                course = course * 180 / pi

                course_update = {"course": course}

                self.mqtt_client.publish(
                    f"{self.topic_prefix}/vel/course",
                    json.dumps(course_update),
                    retain=False,
                    qos=0,
                )

                self.local_copy["course"] = course_update

            m_per_s_2_ft_per_min = 196.85
            climb_rate_update = {"climb_rate_fps": -1 * msg["d"] * m_per_s_2_ft_per_min}

            self.mqtt_client.publish(
                f"{self.topic_prefix}/vel/climbrate",
                json.dumps(climb_rate_update),
                retain=False,
                qos=0,
            )

            self.local_copy["climbrate"] = dict(climb_rate_update)

        except Exception as e:
            logger.exception("FUS: Error fusing vel sources")
            raise e

    def fuse_att_quat(self, msg: dict) -> None:
        """
        Callback for receiving quaternion att data in NED reference frame from vio and publishes into a fusion/att/quat topic.

        VRC doesnt have sophisticated fusion yet, so this just re-routes the message onto the fusion topic.

        """

        try:
            quat_update = {"w": msg["w"], "x": msg["x"], "y": msg["y"], "z": msg["z"]}

            self.mqtt_client.publish(
                f"{self.topic_prefix}/att/quat",
                json.dumps(quat_update),
                retain=False,
                qos=0,
            )

            self.local_copy["quat"] = dict(quat_update)
        except Exception as e:
            logger.exception("FUS: Error fusing att/quat sources")
            raise e

    def fuse_att_euler(self, msg: dict) -> None:
        """
        Callback for receiving euler att data in NED reference frame from vio and publishes into a fusion/att/euler topic.

        VRC doesnt have sophisticated fusion yet, so this just re-routes the message onto the fusion topic.

        """

        try:
            euler_update = {"psi": msg["psi"], "theta": msg["theta"], "phi": msg["phi"]}

            self.mqtt_client.publish(
                f"{self.topic_prefix}/att/euler",
                json.dumps(euler_update),
                retain=False,
                qos=0,
            )

            self.local_copy["euler"] = dict(euler_update)
        except Exception as e:
            logger.exception("FUS: Error fusing att/eul sources")
            raise e

    def fuse_att_heading(self, msg: dict) -> None:
        """
        Callback for receiving heading att data in NED reference frame from vio and publishes into a fusion/att/heading topic.

        VRC doesnt have sophisticated fusion yet, so this just re-routes the message onto the fusion topic.

        """

        try:
            heading_update = {"heading": msg["degrees"]}

            self.mqtt_client.publish(
                f"{self.topic_prefix}/att/heading",
                json.dumps(heading_update),
                retain=False,
                qos=0,
            )
            self.local_copy["heading"] = heading_update["heading"]

            if (
                self.local_copy["groundspeed"]["groundspeed"]
                < self.config["COURSE_THRESHOLD"]
            ):
                self.local_copy["course"] = dict({"course": msg["degrees"]})
        except Exception as e:
            logger.exception("FUS: Error fusing att/heading sources")

    def assemble_hil_gps_message(self) -> None:
        """
        This code takes the pos data from fusion and formats it into a special message that is exactly
        what the FCC needs to generate the hil_gps message (with heading)
        """
        time.sleep(10)
        while not self.vio_init:
            time.sleep(1)
        while True:
            time.sleep(0.1)
            try:
                lat = int(
                    self.local_copy["geo"]["lat"] * 10000000
                )  # convert to int32 format
                lon = int(
                    self.local_copy["geo"]["lon"] * 10000000
                )  # convert to int32 format

                # if lat / lon is 0, that means the ned -> lla conversion hasn't run yet, don't send that data to FCC
                if lat != 0 and lon != 0:
                    hil_gps_update = {
                        "hil_gps": {
                            "time_usec": int(time.time() * 1000000),
                            "fix_type": int(
                                self.config["hil_gps_constants"]["fix_type"]
                            ),  # 3 - 3D fix
                            "lat": lat,
                            "lon": lon,
                            "alt": int(
                                self.local_copy["geo"]["alt"] * 1000
                            ),  # convert m to mm
                            "eph": int(self.config["hil_gps_constants"]["eph"]),  # cm
                            "epv": int(self.config["hil_gps_constants"]["epv"]),  # cm
                            "vel": int(self.local_copy["groundspeed"]["groundspeed"]),
                            "vn": int(self.local_copy["vel"]["Vn"]),
                            "ve": int(self.local_copy["vel"]["Ve"]),
                            "vd": int(self.local_copy["vel"]["Vd"]),
                            "cog": int(self.local_copy["course"]["course"] * 100),
                            "satellites_visible": int(
                                self.config["hil_gps_constants"]["satellites_visible"]
                            ),
                            "heading": int(self.local_copy["heading"] * 100),
                        }
                    }
                    self.mqtt_client.publish(
                        f"{self.topic_prefix}/hil_gps",
                        json.dumps(hil_gps_update),
                        retain=False,
                        qos=0,
                    )

            except Exception as e:
                logger.exception("FUS: Error creating hil_gps_message")
                time.sleep(1)
                # raise e
                continue

    def on_apriltag_message(self, msg: dict) -> None:
        try:
            if self.vio_init:
                now = time.time()
                t265_ned = self.local_copy["pos"]
                t265_heading = self.local_copy["heading"]
                at_ned = msg["pos"]
                at_heading = msg["heading"]

                n_dist = abs(at_ned["n"] - t265_ned["n"])
                e_dist = abs(at_ned["e"] - t265_ned["e"])
                d_dist = abs(at_ned["d"] - t265_ned["d"])

                norm = np.linalg.norm([n_dist, e_dist, d_dist])

                heading_delta = abs(at_heading - t265_heading)
                if heading_delta > 180:
                    heading_delta = 360 - heading_delta

                for idx, val in enumerate(at_ned.keys()):
                    self.deriv[idx] = (at_ned[val] - self.last_pos[idx]) / (
                        now - self.last_apriltag
                    )
                    self.last_pos[idx] = at_ned[val]

                deriv_norm = np.linalg.norm(self.deriv)

                if (
                    self.norm > self.config["POS_DETLA_THRESHOLD"]
                    or abs(heading_delta) > self.config["HEADING_DELTA_THRESHOLD"]
                ) and deriv_norm < self.config["AT_DERIV_THRESH"]:
                    logger.debug(f"FUS: Resync Triggered! Delta={norm}")
                    updates = []

                    if d_dist > self.config["POS_D_THRESHOLD"]:
                        # don't resync Z if del_d is too great, reject AT readings that are extraineous
                        at_ned["d"] = t265_ned["d"]

                    resync = {
                        "n": at_ned["n"],
                        "e": at_ned["e"],
                        "d": at_ned["d"],
                        "heading": at_heading,
                    }
                    self.mqtt_client.publish("vrc/vio/resync", resync)

                self.then = now

        except Exception as e:
            logger.exception("FUS: Error in t265 resync")
            raise e

    def run(self) -> None:
        self.mqtt_client.connect(host=self.mqtt_host, port=self.mqtt_port, keepalive=60)

        hil_thread = threading.Thread(
            target=self.assemble_hil_gps_message,
            args=(),
            daemon=True,
            name="assemble_hil_gps_thread",
        )
        hil_thread.start()

        self.mqtt_client.loop_forever()


if __name__ == "__main__":
    fusion = Fusion()
    fusion.run()
