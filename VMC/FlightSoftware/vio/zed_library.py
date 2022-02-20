from typing import Optional

import pyzed.sl as sl
from loguru import logger


class ZEDCamera(object):
    """
    ZED Tracking Camera interface. Manages pulling data off of the camera for use by the transforms to get it in the correct reference frame.
    """

    def setup(self) -> None:
        try:
            # Create a Camera object
            logger.debug("Starting Camera initialization -- pyzed.sl loaded")

            self.zed = sl.Camera()
            logger.debug("Created Camera obj")

            # Create a InitParameters object and set configuration parameters
            init_params = sl.InitParameters()
            init_params.camera_resolution = (
                sl.RESOLUTION.HD720
            )  # Use HD720 video mode (default fps: 60)
            # Use a right-handed Y-up coordinate system
            init_params.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP
            init_params.coordinate_units = sl.UNIT.METER  # Set units in meters

            # Open the camera
            logger.debug("Zed Camera Loading...")
            err = self.zed.open(init_params)

            if err != sl.ERROR_CODE.SUCCESS:
                logger.debug("Zed Camera Loadng (FAILED!!!)")
                exit(1)
            logger.debug("Zed Camera Loaded/open (Success)")

            # Enable positional tracking with default parameters
            py_transform = (
                sl.Transform()
            )  # First create a Transform object for TrackingParameters object
            self.tracking_parameters = sl.PositionalTrackingParameters(
                _init_pos=py_transform
            )
            self.tracking_parameters.set_floor_as_origin = True
            err = self.zed.enable_positional_tracking(self.tracking_parameters)
            if err != sl.ERROR_CODE.SUCCESS:
                exit(1)

            logger.debug("Zed Camera Enabled positional tracking")

            # Track the camera position during 1000 frames
            i = 0
            self.zed_pose = sl.Pose()
            self.zed_sensors = sl.SensorsData()
            self.zed.get_position(self.zed_pose, sl.REFERENCE_FRAME.WORLD)
            self.zed.get_sensors_data(self.zed_sensors, sl.TIME_REFERENCE.IMAGE)
            self.zed_imu = self.zed_sensors.get_imu_data()
            self.last_pos = [0, 0, 0]

            self.runtime_parameters = sl.RuntimeParameters()
            self.last_time = 0
        except Exception as e:
            logger.exception(f"ZED: Error connecting to ZED Camera: {e}")
            raise e

    def get_pipe_data(self) -> Optional[dict]:
        if self.zed.grab(self.runtime_parameters) != sl.ERROR_CODE.SUCCESS:
            return

        try:
            # logger.debug("Zed Camera Successfully grabbed params")
            # Get the pose of the left eye of the camera with reference to the world frame
            self.zed.get_position(self.zed_pose, sl.REFERENCE_FRAME.WORLD)
            # logger.debug("Zed Camera Successfully go position data")

            self.zed.get_sensors_data(self.zed_sensors, sl.TIME_REFERENCE.IMAGE)
            # logger.debug("Zed Camera Successfully got sensor data")

            self.zed_imu = self.zed_sensors.get_imu_data()

            # Retrieve the translation
            py_translation = sl.Translation()
            tx = self.zed_pose.get_translation(py_translation).get()[0]
            ty = self.zed_pose.get_translation(py_translation).get()[1]
            tz = self.zed_pose.get_translation(py_translation).get()[2]
            # logger.debug("Translation: Tx: {0}, Ty: {1}, Tz {2}, Timestamp: {3}\n".format(tx, ty, tz, self.zed_pose.timestamp.get_milliseconds()))

            # Calculate Velocity

            current_time = self.zed.get_timestamp(
                sl.TIME_REFERENCE.IMAGE
            ).get_milliseconds()
            diffx = tx - self.last_pos[0]
            diffy = ty - self.last_pos[1]
            diffz = tz - self.last_pos[2]
            time_diff = (current_time - self.last_time) / 1000
            # logger.debug("velocity calc ->:timediff: {0}  x: {1}, y: {2}, z {3}\n".format(time_diff, diffx, diffy, diffz))
            velocity = [diffx / time_diff, diffy / time_diff, diffz / time_diff]
            self.last_time = current_time
            self.last_pos[0] = tx
            self.last_pos[1] = ty
            self.last_pos[2] = tz

            # get orientation
            py_orientation = sl.Orientation()
            orotation = self.zed_pose.get_orientation(py_orientation)
            # fix backwards y
            o = sl.Orientation()
            # fixing y rotation problem -- need to investigate
            o.init_vector(
                orotation.get()[0],
                orotation.get()[1] * -1,
                orotation.get()[2],
                orotation.get()[3],
            )
            rotation = o.get()

            # assemble return value
            translation = {"x": tx, "y": ty, "z": tz}
            return {
                "rotation": rotation,
                "translation": translation,
                "velocity": velocity,
                "tracker_confidence": 0x3,
                "mapper_confidence": 0x3,
            }

        except OSError as err:
            logger.debug(f"OS error: {err}")
        except ValueError as err:
            logger.debug(f"Could not convert data: {err}, {type(err)}")
        except BaseException as err:
            logger.debug(f"Unexpected {err}, {type(err)}")
            raise
