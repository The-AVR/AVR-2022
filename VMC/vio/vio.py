import math
from typing import Tuple

import numpy as np
from bell.avr.mqtt.client import MQTTModule
from bell.avr.mqtt.payloads import (
    AvrVioConfidencePayload,
    AvrVioHeadingPayload,
    AvrVioOrientationEulPayload,
    AvrVioPositionNedPayload,
    AvrVioResyncPayload,
    AvrVioVelocityNedPayload,
)
from bell.avr.utils.decorators import run_forever, try_except
from loguru import logger
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
        self.topic_map = {"avr/vio/resync": self.handle_resync}

    def handle_resync(self, payload: AvrVioResyncPayload) -> None:
        # whenever new data is published to the ZEDCamera resync topic, we need to compute a new correction
        # to compensate for sensor drift over time.
        if not self.init_sync or self.continuous_sync:
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
    ) -> None:
        if np.isnan(ned_pos).any():
            raise ValueError("ZEDCamera has NaNs for position")

        # send position update
        n = float(ned_pos[0])
        e = float(ned_pos[1])
        d = float(ned_pos[2])
        ned_update = AvrVioPositionNedPayload(n=n, e=e, d=d)  # cm

        self.send_message("avr/vio/position/ned", ned_update)

        if np.isnan(rpy).any():
            raise ValueError("Camera has NaNs for orientation")

        # send orientation update
        eul_update = AvrVioOrientationEulPayload(psi=rpy[0], theta=rpy[1], phi=rpy[2])
        self.send_message("avr/vio/orientation/eul", eul_update)

        # send heading update
        heading = rpy[2]
        # correct for negative heading
        if heading < 0:
            heading += 2 * math.pi
        heading = np.rad2deg(heading)
        heading_update = AvrVioHeadingPayload(degrees=heading)
        self.send_message("avr/vio/heading", heading_update)
        # coord_trans.heading = rpy[2]

        if np.isnan(ned_vel).any():
            raise ValueError("Camera has NaNs for velocity")

        # send velocity update
        vel_update = AvrVioVelocityNedPayload(n=ned_vel[0], e=ned_vel[1], d=ned_vel[2])
        self.send_message("avr/vio/velocity/ned", vel_update)

        confidence_update = AvrVioConfidencePayload(
            tracker=tracker_confidence,
        )
        self.send_message("avr/vio/confidence", confidence_update)

    @run_forever(frequency=10)
    @try_except(reraise=False)
    def process_camera_data(self) -> None:
        data = self.camera.get_pipe_data()

        if data is None:
            logger.debug("Waiting on camera data")
            return

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
