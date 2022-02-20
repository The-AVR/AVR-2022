import copy
import math
import threading
import time

import numpy as np
import pymap3d
from decorator_library import try_except
from loguru import logger
from mqtt_library import MQTTModule


class FusionModule(MQTTModule):
    def __init__(self):
        super().__init__()

        self.config = {
            # Bell HQ VIP helipad
            # https://www.google.com/maps/place/32%C2%B048'30.8%22N+97%C2%B009'22.8%22W
            "origin": {"lat": 32.808549, "lon": -97.156345, "alt": 161.5},
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
            "AT_DERIV_THRESHOLD": 10,
        }

        self.topic_map = {
            "vrc/vio/position/ned": self.fuse_pos,
            "vrc/vio/orientation/eul": self.fuse_att_euler,
            "vrc/vio/heading": self.fuse_att_heading,
            "vrc/vio/velocity/ned": self.fuse_vel,
            "vrc/fusion/pos/ned": self.local_to_geo,
            # "apriltags/selected/pos": self.on_apriltag_message
        }

        self.vio_init = False

        # on_apriltag storage
        self.norm = None
        self.last_pos = [0, 0, 0]
        self.deriv = [0, 0, 0]
        self.last_apriltag = time.time()

    @try_except(reraise=True)
    def local_to_geo(self, payload: dict) -> None:
        """
        Callback for the fusion/pos topic. This method calculates the
        geodetic location from an NED position and origin and publishes it.
        """
        lla = pymap3d.enu2geodetic(
            float(payload["e"]) / 100,  # type: ignore # East   | Y
            float(payload["n"]) / 100,  # type: ignore # North  | X
            -1 * float(payload["d"]) / 100,  # type: ignore # Up     | Z
            self.config["origin"]["lat"],  # Origin lat
            self.config["origin"]["lon"],  # Origin lon
            self.config["origin"]["alt"],  # Origin alt
            deg=True,
        )

        geo_update = {"geodetic": {"lat": lla[0], "lon": lla[1], "alt": lla[2]}}
        self.send_message("vrc/fusion/geo", geo_update)

    @try_except(reraise=True)
    def fuse_pos(self, msg: dict) -> None:
        """
        Callback for receiving pos data in NED reference frame from VIO and
        publishes into a fusion/pos topic.

        VRC doesnt have sophisticated fusion yet, so this just re-routes the
        message onto the fusion topic.
        """

        pos_update = {"n": msg["n"], "e": msg["e"], "d": msg["d"]}
        self.send_message("vrc/fusion/pos/ned", pos_update)

    @try_except(reraise=True)
    def fuse_vel(self, msg: dict) -> None:
        """
        Callback for receiving vel data in NED reference frame from VIO and
        publishes into a fusion/vel topic.

        VRC doesnt have sophisticated fusion yet, so this just re-routes the
        message onto the fusion topic.
        """
        # record that VIO has initialized
        self.vio_init = True

        # forward ned velocity message
        vmc_vel_update = {"Vn": msg["n"], "Ve": msg["e"], "Vd": msg["d"]}
        self.send_message("vrc/fusion/vel/ned", vmc_vel_update)

        # compute groundspeed
        gs = np.linalg.norm([msg["n"], msg["e"]])
        groundspeed_update = {"groundspeed": gs}
        self.send_message("vrc/fusion/groundspeed", groundspeed_update)

        # arctan gets real noisy when the values get small, so we just lock course
        # to heading when we aren't really moving
        if gs >= self.config["COURSE_THRESHOLD"]:
            course = math.atan2(msg["e"], msg["n"])
            # wrap [-pi, pi] to [0, 360]
            if course < 0:
                course += 2 * math.pi

            # rad to deg
            course = math.degrees(course)
            course_update = {"course": course}

            self.send_message("vrc/fusion/course", course_update)

        m_per_s_2_ft_per_min = 196.85
        climb_rate_update = {"climb_rate_fps": -1 * msg["d"] * m_per_s_2_ft_per_min}

        self.send_message("vrc/fusion/climbrate", climb_rate_update)

    @try_except(reraise=True)
    def fuse_att_quat(self, msg: dict) -> None:
        """
        Callback for receiving quaternion att data in NED reference frame
        from vio and publishes into a fusion/att/quat topic.

        VRC doesnt have sophisticated fusion yet, so this just re-routes
        the message onto the fusion topic.
        """
        quat_update = {"w": msg["w"], "x": msg["x"], "y": msg["y"], "z": msg["z"]}
        self.send_message("vrc/fusion/att/quat", quat_update)

    @try_except(reraise=True)
    def fuse_att_euler(self, msg: dict) -> None:
        """
        Callback for receiving euler att data in NED reference frame from VIO and
        publishes into a fusion/att/euler topic.

        VRC doesnt have sophisticated fusion yet, so this just re-routes
        the message onto the fusion topic.
        """
        euler_update = {"psi": msg["psi"], "theta": msg["theta"], "phi": msg["phi"]}
        self.send_message("vrc/fusion/att/euler", euler_update)

    @try_except(reraise=True)
    def fuse_att_heading(self, msg: dict) -> None:
        """
        Callback for receiving heading att data in NED reference frame from VIO and
        publishes into a fusion/att/heading topic.

        VRC doesnt have sophisticated fusion yet, so this just re-routes
        the message onto the fusion topic.
        """
        heading_update = {"heading": msg["degrees"]}
        self.send_message("vrc/fusion/att/heading", heading_update)

        # if the groundspeed is below the threshold, we lock the course to the heading
        if (
            self.message_cache["vrc/fusion/vel/groundspeed"]["groundspeed"]
            < self.config["COURSE_THRESHOLD"]
        ):
            self.message_cache["vrc/fusion/vel/course"] = copy.deepcopy(
                {"course": msg["degrees"]}
            )

    @try_except(reraise=False)
    def assemble_hil_gps_message(self) -> None:
        """
        This code takes the pos data from fusion and formats it into a special
        message that is exactly what the FCC needs to generate the hil_gps message
        (with heading)
        """
        while not self.vio_init:
            logger.debug("Waiting for VIO to initialize")
            time.sleep(1)

        while True:
            time.sleep(0.1)

            goedetic = self.message_cache["vrc/fusion/geo"]["geodetic"]
            lat = int(goedetic["lat"] * 10000000)  # convert to int32 format
            lon = int(goedetic["lon"] * 10000000)  # convert to int32 format

            # if lat / lon is 0, that means the ned -> lla conversion hasn't run yet,
            # don't send that data to FCC
            if lat == 0 or lon == 0:
                continue

            hil_gps_update = {
                "hil_gps": {
                    "time_usec": int(time.time() * 1000000),
                    "fix_type": int(
                        self.config["hil_gps_constants"]["fix_type"]
                    ),  # 3 - 3D fix
                    "lat": lat,
                    "lon": lon,
                    "alt": int(
                        self.message_cache["geo"]["geodetic"]["alt"] * 1000
                    ),  # convert m to mm
                    "eph": int(self.config["hil_gps_constants"]["eph"]),  # cm
                    "epv": int(self.config["hil_gps_constants"]["epv"]),  # cm
                    "vel": int(self.message_cache["groundspeed"]["groundspeed"]),
                    "vn": int(self.message_cache["vel"]["Vn"]),
                    "ve": int(self.message_cache["vel"]["Ve"]),
                    "vd": int(self.message_cache["vel"]["Vd"]),
                    "cog": int(self.message_cache["course"]["course"] * 100),
                    "satellites_visible": int(
                        self.config["hil_gps_constants"]["satellites_visible"]
                    ),
                    "heading": int(
                        self.message_cache["vrc/fusion/att/heading"]["heading"] * 100
                    ),
                }
            }
            self.send_message("vrc/fusion/hil_gps", hil_gps_update)

    @try_except(reraise=True)
    def on_apriltag_message(self, msg: dict) -> None:
        # wait for VIO to initialize
        if not self.vio_init:
            return

        now = time.time()

        # pull ned and heading from cache
        cam_ned = self.message_cache["vrc/fusion/pos/ned"]
        cam_heading = self.message_cache["vrc/fusion/att/heading"]
        # get april tag ned and heading
        at_ned = msg["pos"]
        at_heading = msg["heading"]

        # compute differences
        n_dist = abs(at_ned["n"] - cam_ned["n"])
        e_dist = abs(at_ned["e"] - cam_ned["e"])
        d_dist = abs(at_ned["d"] - cam_ned["d"])

        norm = np.linalg.norm([n_dist, e_dist, d_dist])

        heading_delta = abs(at_heading - cam_heading)
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
        ) and deriv_norm < self.config["AT_DERIV_THRESHOLD"]:
            logger.debug(f"Resync Triggered! Delta={norm}")

            if d_dist > self.config["POS_D_THRESHOLD"]:
                # don't resync Z if del_d is too great,
                # reject AT readings that are extraineous
                at_ned["d"] = cam_ned["d"]

            resync = {
                "n": at_ned["n"],
                "e": at_ned["e"],
                "d": at_ned["d"],
                "heading": at_heading,
            }
            self.send_message("vrc/vio/resync", resync)

        self.last_apriltag = now

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
    fusion = FusionModule()
    fusion.run()
