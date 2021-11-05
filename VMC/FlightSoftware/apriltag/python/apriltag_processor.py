import json
import subprocess
import threading
import time
import warnings
from math import atan2, degrees, pi
from typing import Any, Union

import numpy as np
import paho.mqtt.client as mqtt
import transforms3d as t3d
from loguru import logger

# find the file path to this file
# __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

warnings.simplefilter("ignore", np.RankWarning)


# [{
#     "id": 0,
#     "pos": {
#         "x": -0.08439404,
#         "y": 0.34455082,
#         "z": 1.1740385
#     },
#     "rotation": [
#         [
#             -0.71274376,
#             -0.47412094,
#             -0.5169194
#         ],
#         [
#             0.054221954,
#             -0.7719936,
#             0.6333134
#         ],
#         [
#             -0.6993256,
#             0.4233618,
#             0.5759414
#         ]
#     ]
# }]


class VRCAprilTag(object):
    def __init__(self):
        self.default_config: dict = {
            "cam": {
                "pos": [13, 0, 8.5],  # cm from FC forward, right, down
                "rpy": [
                    0,
                    0,
                    -pi / 2,
                ],  # cam x = body -y; cam y = body x, cam z = body z
            },
            "tag_truth": {"0": {"rpy": [0, 0, 0], "xyz": [0, 0, 0]}},
            "AT_UPDATE_FREQ": 5,
            "AT_HEARTBEAT_THRESH": 0.25,
        }

        self.tm = dict()

        self.setup_transforms()

        self.pos_array = {"n": [], "e": [], "d": [], "heading": [], "time": []}

        self.mqtt_host = "mqtt"
        self.mqtt_port = 18830

        # self.mqtt_user = "user"
        # self.mqtt_pass = "password"

        self.mqtt_client = mqtt.Client()
        # self.mqtt_client.username_pw_set(
        #     username=self.mqtt_user, password=self.mqtt_pass
        # )

        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message

        self.topic_prefix = "vrc/apriltags"
        self.topic_map = {f"{self.topic_prefix}/raw": self.on_apriltag_message}

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
        logger.debug(f"Connected with result code {rc}")
        for topic in self.topic_map.keys():
            logger.debug(f"Apriltag Module: Subscribed to: {topic}")
            client.subscribe(topic)

    def run_mqtt(self):
        self.mqtt_client.connect(host=self.mqtt_host, port=self.mqtt_port, keepalive=60)
        self.mqtt_client.loop_forever()

    def setup_transforms(self):
        rmat = t3d.euler.euler2mat(
            self.default_config["cam"]["rpy"][0],
            self.default_config["cam"]["rpy"][1],
            self.default_config["cam"]["rpy"][2],
            axes="rxyz",
        )  # type: ignore
        H_cam_aeroBody = t3d.affines.compose(self.default_config["cam"]["pos"], rmat, [1, 1, 1])  # type: ignore

        H_aeroBody_cam = np.linalg.inv(H_cam_aeroBody)
        self.tm["H_aeroBody_cam"] = H_aeroBody_cam

        for tag in self.default_config["tag_truth"]:  # type: ignore
            name = "tag_" + tag
            tag_dat = self.default_config["tag_truth"][tag]  # type: ignore
            rmat = t3d.euler.euler2mat(tag_dat["rpy"][0], tag_dat["rpy"][1], tag_dat["rpy"][2], axes="rxyz")  # type: ignore
            tag_tf = t3d.affines.compose(tag_dat["xyz"], rmat, [1, 1, 1])  # type: ignore

            H_to_from = "H_" + name + "_aeroRef"
            self.tm[H_to_from] = tag_tf
            H_to_from = "H_" + name + "_cam"
            self.tm[H_to_from] = np.eye(4)

    def on_apriltag_message(self, payload):
        tag_list = []

        min_dist = 1000000

        closest_tag = None

        for index, tag in enumerate(payload):

            (
                id,
                horizontal_distance,
                vertical_distance,
                angle,
                pos_world,
                pos_rel,
                heading,
            ) = self.handle_tag(tag)

            # weird special case (this shouldn't really happen though?)
            if id is None:
                continue

            tag = {
                "id": id,
                "horizontal_dist": horizontal_distance,
                "vertical_dist": vertical_distance,
                "angle_to_tag": angle,
                "heading": heading,
                "pos_rel": {
                    "x": pos_rel[0],
                    "y": pos_rel[1],
                    "z": pos_rel[2],
                },
            }

            # add some more info if we had the truth data for the tag
            if pos_world is not None:
                if pos_world.any():

                    tag["pos_world"] = {
                        "x": pos_world[0],  # type: ignore
                        "y": pos_world[1],  # type: ignore
                        "z": pos_world[2],  # type: ignore
                    }
                    if horizontal_distance < min_dist:
                        min_dist = horizontal_distance
                        closest_tag = index

            tag_list.append(tag)

        self.mqtt_client.publish(
            f"{self.topic_prefix}/visible_tags", json.dumps(tag_list)
        )

        if closest_tag is not None:
            apriltag_position = {
                "tag_id": tag_list[closest_tag]["id"],  # type: ignore
                "pos": {
                    "n": tag_list[closest_tag]["pos_world"]["x"],  # type: ignore
                    "e": tag_list[closest_tag]["pos_world"]["y"],  # type: ignore
                    "d": tag_list[closest_tag]["pos_world"]["z"],  # type: ignore
                },
                "heading": tag_list[closest_tag]["heading"],  # type: ignore
            }

            self.mqtt_client.publish(
                f"{self.topic_prefix}/selected", json.dumps(apriltag_position)
            )

    def angle_to_tag(self, pos):
        deg = degrees(
            atan2(pos[1], pos[0])
        )  # TODO - i think plus pi/2 bc this is respect to +x

        if deg < 0.0:
            deg += 360.0

        return deg

    def world_angle_to_tag(self, pos, tag_id) -> Union[float, None]:
        """
        returns the angle with respect to "north" in the "world frame"
        """
        if str(tag_id) in self.default_config["tag_truth"].keys():
            del_x = self.default_config["tag_truth"][str(tag_id)]["xyz"][0] - pos[0]
            del_y = self.default_config["tag_truth"][str(tag_id)]["xyz"][1] - pos[1]
            deg = degrees(
                atan2(del_y, del_x)
            )  # TODO - i think plus pi/2 bc this is respect to +x

            if deg < 0.0:
                deg += 360.0

            return deg

    def H_inv(self, H: t3d.affines) -> t3d.affines:
        """
        a method to efficiently compute the inverse of a homogeneous transformation matrix
        for reference: http://vr.cs.uiuc.edu/node81.html
        """

        T, R, Z, S = t3d.affines.decompose44(H)

        R_t = np.transpose(R)
        H_rot = t3d.affines.compose(
            [0, 0, 0],
            R_t,
            [1, 1, 1],
        )
        H_tran = t3d.affines.compose(
            [-1 * T[0], -1 * T[1], -1 * T[2]],
            np.eye(3),
            [1, 1, 1],
        )

        return H_rot.dot(H_tran)

    def handle_tag(self, tag):
        """
        Calculates the distance, position, and heading of the drone in NED frame
        based on the tag detections.
        """
        tag_id = tag["id"]

        tag_rot = np.asarray(tag["rotation"])
        rpy = t3d.euler.mat2euler(tag_rot)
        R = t3d.euler.euler2mat(0, 0, rpy[2], axes="rxyz")
        H_tag_cam = t3d.affines.compose(
            [tag["pos"]["x"] * 100, tag["pos"]["y"] * 100, tag["pos"]["z"] * 100],
            R,
            [1, 1, 1],
        )
        T, R, Z, S = t3d.affines.decompose44(H_tag_cam)

        name = "tag_" + str(tag_id)
        H_to_from = "H_" + name + "_cam"
        self.tm[H_to_from] = H_tag_cam

        # H_cam_tag = np.linalg.inv(H_tag_cam)
        H_cam_tag = self.H_inv(H_tag_cam)

        H_aerobody_tag = H_cam_tag.dot(self.tm["H_aeroBody_cam"])  # type: ignore

        T2, R2, Z2, S2 = t3d.affines.decompose44(H_aerobody_tag)
        rpy = t3d.euler.mat2euler(R2)
        pos_rel = T2

        horizontal_distance = np.linalg.norm([pos_rel[0], pos_rel[1]])
        vertical_distance = abs(pos_rel[2])

        heading = rpy[2]
        if heading < 0:
            heading += 2 * pi

        heading = np.rad2deg(heading)
        angle = self.angle_to_tag(pos_rel)

        # if we have a location definition for the visible tag
        if str(tag["id"]) in self.default_config["tag_truth"].keys():

            H_cam_aeroRef = self.tm["H_" + name + "_aeroRef"].dot(H_cam_tag)

            H_aeroBody_aeroRef = H_cam_aeroRef.dot(self.tm["H_aeroBody_cam"])

            pos_world, R, Z, S = t3d.affines.decompose44(H_aeroBody_aeroRef)

            return (
                tag_id,
                horizontal_distance,
                vertical_distance,
                angle,
                pos_world,
                pos_rel,
                heading,
            )
        else:
            return (
                tag_id,
                horizontal_distance,
                vertical_distance,
                angle,
                None,
                pos_rel,
                heading,
            )

    def main(self):
        # tells the os what to name this process, for debugging
        subprocess.Popen("./vrcapriltags", cwd="./c/build", shell=True)

        threads = []
        mqtt_thread = threading.Thread(
            target=self.run_mqtt, args=(), daemon=True, name="apriltag_mqtt_thread"
        )
        threads.append(mqtt_thread)

        for thread in threads:
            thread.start()
            logger.debug(f"AT: starting thread: {thread.name}")

        while True:
            time.sleep(0.1)


if __name__ == "__main__":
    atag = VRCAprilTag()
    atag.main()
