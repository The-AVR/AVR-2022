import math
import copy
from typing import Tuple, List

import numpy as np
import transforms3d as t3d
from loguru import logger

from decorator_library import try_except


class CameraCoordinateTransformation:
    """
    This class handles all the coordinate transformations we need to use to get
    relevant data from the tracking camera
    """

    def __init__(self):
        self.config: dict = {
            "cam": {
                "pos": [17, 0, 8.5],  # cm from FC forward, right, down
                "rpy": [
                    0,
                    -math.pi / 2,
                    -math.pi / 2,
                ],  # cam x = body -y; cam y = body x, cam z = body z
                "ground_height": 10,  # cm
            }
        }

        # dict to hold transformation matrixes
        self.tm = {}
        # setup transformation matrixes
        self.setup_transforms()

    def setup_transforms(self) -> None:
        cam_rpy = self.config["cam"]["rpy"]

        H_aeroBody_ZEDCAMBody = t3d.affines.compose(
            self.config["cam"]["pos"],
            t3d.euler.euler2mat(
                cam_rpy[0],
                cam_rpy[1],
                cam_rpy[2],
                axes="rxyz",
            ),
            [1, 1, 1],
        )
        self.tm["H_aeroBody_ZEDCAMBody"] = H_aeroBody_ZEDCAMBody
        self.tm["H_ZEDCAMBody_aeroBody"] = np.linalg.inv(H_aeroBody_ZEDCAMBody)

        pos = copy.deepcopy(self.config["cam"]["pos"])
        pos[2] = -1 * self.config["cam"]["ground_height"]

        H_aeroRef_ZEDCAMRef = t3d.affines.compose(
            pos,
            t3d.euler.euler2mat(
                cam_rpy[0],
                cam_rpy[1],
                cam_rpy[2],
                axes="rxyz",
            ),
            [1, 1, 1],
        )
        self.tm["H_aeroRef_ZEDCAMRef"] = H_aeroRef_ZEDCAMRef

        H_aeroRefSync_aeroRef = np.eye(4)
        self.tm["H_aeroRefSync_aeroRef"] = H_aeroRefSync_aeroRef

        H_nwu_aeroRef = t3d.affines.compose(
            [0, 0, 0], t3d.euler.euler2mat(math.pi, 0, 0), [1, 1, 1]
        )
        self.tm["H_nwu_aeroRef"] = H_nwu_aeroRef

    def sync(self, heading_ref, pos_ref):
        """
        Computes offsets between zedcamera ref and "global" frames, to align coord. systems
        """
        # get current readings on where the aeroBody is, according to the sensor
        H = self.tm["H_aeroRef_aeroBody"]
        T, R, Z, S = t3d.affines.decompose44(H)
        eul = t3d.euler.mat2euler(R, axes="rxyz")

        ## Find the heading offset...
        heading = eul[2]

        # wrap heading in (0, 2*pi)
        if heading < 0:
            heading += 2 * math.pi

        # compute the difference between our global reference, and what our sensor is reading for heading
        heading_offset = heading_ref - (math.degrees(heading))
        logger.debug(f"ZEDCAM: Resync: Heading Offset:{heading_offset}")

        # build a rotation matrix about the global Z axis to apply the heading offset we computed
        H_rot_correction = t3d.affines.compose(
            [0, 0, 0],
            t3d.axangles.axangle2mat([0, 0, 1], math.radians(heading_offset)),
            [1, 1, 1],
        )

        # apply the heading correction to the position data the ZEDCAM is providing
        H = H_rot_correction.dot(H)
        T, R, Z, S = t3d.affines.decompose44(H)
        eul = t3d.euler.mat2euler(R, axes="rxyz")

        ## Find the position offset
        pos_offset = [pos_ref["n"] - T[0], pos_ref["e"] - T[1], pos_ref["d"] - T[2]]
        logger.debug(f"ZEDCAM: Resync: Pos offset:{pos_offset}")

        # build a translation matrix that corrects the difference between where the sensor thinks we are and were our reference thinks we are
        H_aeroRefSync_aeroRef = t3d.affines.compose(
            pos_offset, H_rot_correction[:3, :3], [1, 1, 1]
        )
        self.tm["H_aeroRefSync_aeroRef"] = H_aeroRefSync_aeroRef

    @try_except(reraise=False)
    def transform_zedcamera_to_global_ned(
        self, data: dict
    ) -> Tuple[List[float], np.ndarray, Tuple[float, float, float]]:
        """
        Takes in raw sensor data from the camera frame, does the necessary
        transformations between the sensor, vehicle, and reference frames to
        present the sensor data in the "global" NED reference frame.

        Arguments:
        --------------------------
        data : Camera Frame data

        Returns:
        --------------------------
        pos: list
            The NED position of the vehice. A 3 unit list [north, east, down]
        vel: list
            The NED velocities of the vehicle. A 3 unit list [Vn, Ve, Vd]
        rpy: list
            The euler representation of the vehicle attitude.
            A 3 unit list [roll,math.pitch, yaw]

        """
        quaternion = data["rotation"]

        position = [
            data["translation"]["x"] * 100,
            data["translation"]["y"] * 100,
            data["translation"]["z"] * 100,
        ]  # cm

        velocity = np.transpose(
            [
                data["velocity"][0] * 100,
                data["velocity"][1] * 100,
                data["velocity"][2] * 100,
                0,
            ]
        )  # cm/s

        H_ZEDCAMRef_ZEDCAMBody = t3d.affines.compose(
            position, t3d.quaternions.quat2mat(quaternion), [1, 1, 1]
        )

        self.tm["H_ZEDCAMRef_ZEDCAMBody"] = H_ZEDCAMRef_ZEDCAMBody

        H_aeroRef_aeroBody = self.tm["H_aeroRef_ZEDCAMRef"].dot(
            self.tm["H_ZEDCAMRef_ZEDCAMBody"].dot(self.tm["H_ZEDCAMBody_aeroBody"])
        )

        self.tm["H_aeroRef_aeroBody"] = H_aeroRef_aeroBody

        H_aeroRefSync_aeroBody = self.tm["H_aeroRefSync_aeroRef"].dot(
            H_aeroRef_aeroBody
        )
        self.tm["H_aeroRefSync_aeroBody"] = H_aeroRefSync_aeroBody

        T, R, Z, S = t3d.affines.decompose44(H_aeroRefSync_aeroBody)
        eul = t3d.euler.mat2euler(R, axes="rxyz")

        H_vel = self.tm["H_aeroRefSync_aeroRef"].dot(self.tm["H_aeroRef_ZEDCAMRef"])

        vel = np.transpose(H_vel.dot(velocity))

        return T, vel, eul
