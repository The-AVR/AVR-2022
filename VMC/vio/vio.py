import math
import time
from typing import Tuple

import numpy as np
from decorator_library import try_except
from loguru import logger
from mqtt_library import (
    MQTTModule,
    VrcVioConfidenceMessage,
    VrcVioHeadingMessage,
    VrcVioOrientationEulMessage,
    VrcVioPositionNedMessage,
    VrcVioResyncMessage,
    VrcVioVelocityNedMessage,
)
from vio_library import CameraCoordinateTransformation
from zed_library import ZEDCamera


class VIOModule(MQTTModule):
    def __init__(self):
        super().__init__()

        # settings
        self.init_sync = False
        self.continuous_sync = True
        self.CAM_UPDATE_FREQ = 10

        # connected libraries
        self.camera = ZEDCamera()
        self.coord_trans = CameraCoordinateTransformation()

        # mqtt
        self.topic_map = {"vrc/vio/resync": self.handle_resync}

    def handle_resync(self, payload: VrcVioResyncMessage) -> None:
        # whenever new data is published to the ZEDCamera resync topic, we need to compute a new correction
        # to compensate for sensor drift over time.
        if self.init_sync == False or self.continuous_sync == True:
            heading_ref = payload["heading"]
            self.coord_trans.sync(
                heading_ref, {"n": payload["n"], "e": payload["e"], "d": payload["d"]}
            )
            self.init_sync = True

    @try_except(reraise=False)
    def publish_updates(
        self,
        ned_pos: Tuple[float, float, float],
        ned_vel: Tuple[float, float, float],
        rpy: Tuple[float, float, float],
        tracker_confidence: float,
        mapper_confidence: float,
    ) -> None:
        if np.isnan(ned_pos).any():
            raise ValueError("ZEDCamera has NaNs for position")

        # send position update
        n = float(ned_pos[0])
        e = float(ned_pos[1])
        d = float(ned_pos[2])
        ned_update = VrcVioPositionNedMessage(n=n, e=e, d=d)  # cm

        self.send_message("vrc/vio/position/ned", ned_update)

        if np.isnan(rpy).any():
            raise ValueError("Camera has NaNs for orientation")

        # send orientation update
        eul_update = VrcVioOrientationEulMessage(psi=rpy[0], theta=rpy[1], phi=rpy[2])
        self.send_message("vrc/vio/orientation/eul", eul_update)

        # send heading update
        heading = rpy[2]
        # correct for negative heading
        if heading < 0:
            heading += 2 * math.pi
        heading = np.rad2deg(heading)
        heading_update = VrcVioHeadingMessage(degrees=heading)
        self.send_message("vrc/vio/heading", heading_update)
        # coord_trans.heading = rpy[2]

        if np.isnan(ned_vel).any():
            raise ValueError("Camera has NaNs for velocity")

        # send velocity update
        vel_update = VrcVioVelocityNedMessage(n=ned_vel[0], e=ned_vel[1], d=ned_vel[2])
        self.send_message("vrc/vio/velocity/ned", vel_update)

        confidence_update = VrcVioConfidenceMessage(
            mapper=mapper_confidence,
            tracker=tracker_confidence,
        )
        self.send_message("vrc/vio/confidence", confidence_update)

    @try_except(reraise=False)
    def process_camera_data(self) -> None:
        # start the loop
        logger.debug("Beginning data loop")
        while True:
            time.sleep(1 / self.CAM_UPDATE_FREQ)
            data = self.camera.get_pipe_data()

            if data is None:
                continue

            # collect data from the sensor and transform it into "global" NED frame
            (
                ned_pos,
                ned_vel,
                rpy,
            ) = self.coord_trans.transform_trackcamera_to_global_ned(data)

            self.publish_updates(
                ned_pos,
                ned_vel,
                rpy,
                data["tracker_confidence"],
                data["mapper_confidence"],
            )

    def run(self) -> None:
        self.run_non_blocking()

        # setup the tracking camera
        logger.debug("Setting up camera connection")
        self.camera.setup()

        # begin processing data
        self.process_camera_data()


if __name__ == "__main__":
    vio = VIOModule()
    vio.run()
