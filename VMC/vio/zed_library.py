from typing import Optional, Tuple, TypedDict

# Getting pyzed installed in a dev environment is very painful unless
# you already have CUDA and the ZED SDK installed.
import pyzed.sl as sl  # type: ignore
from bell.avr.utils.decorators import try_except
from loguru import logger


class ZedPipeDataTranslation(TypedDict):
    x: float
    y: float
    z: float


class ZedPipeData(TypedDict):
    rotation: Tuple[float, float, float, float]  # quaternion
    translation: ZedPipeDataTranslation
    velocity: Tuple[float, float, float]
    tracker_confidence: float


# Largely adapted from this
# https://github.com/stereolabs/zed-examples/blob/master/tutorials/tutorial%204%20-%20positional%20tracking/python/positional_tracking.py
class ZEDCamera(object):
    """
    ZED Tracking Camera interface.
    Manages pulling data off of the camera for use by the transforms to
    get it in the correct reference frame.
    """

    @try_except(reraise=True)
    def setup(self) -> None:
        # Create a Camera object
        self.zed = sl.Camera()

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
        logger.success("Zed Camera Loaded")

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

        # create class attributes to hold the camera data
        # i'm not really sure, Zed API is super weird
        self.zed_pose = sl.Pose()
        self.zed_sensors = sl.SensorsData()

        self.zed.get_position(self.zed_pose, sl.REFERENCE_FRAME.WORLD)
        self.zed.get_sensors_data(self.zed_sensors, sl.TIME_REFERENCE.IMAGE)
        self.last_pos = [0, 0, 0]

        self.runtime_parameters = sl.RuntimeParameters()
        self.last_time = 0

    @try_except(reraise=True)
    def get_pipe_data(self) -> Optional[ZedPipeData]:
        if self.zed.grab(self.runtime_parameters) != sl.ERROR_CODE.SUCCESS:
            logger.warning("ZED Camera Grab Failed")
            return

        # Get the pose of the left eye of the camera with reference to the world frame
        self.zed.get_position(self.zed_pose, sl.REFERENCE_FRAME.WORLD)
        self.zed.get_sensors_data(self.zed_sensors, sl.TIME_REFERENCE.IMAGE)

        # Retrieve the translation
        py_translation = sl.Translation()
        tx = self.zed_pose.get_translation(py_translation).get()[0]
        ty = self.zed_pose.get_translation(py_translation).get()[1]
        tz = self.zed_pose.get_translation(py_translation).get()[2]

        # Calculate Velocity
        current_time = self.zed.get_timestamp(
            sl.TIME_REFERENCE.IMAGE
        ).get_milliseconds()
        diffx = tx - self.last_pos[0]
        diffy = ty - self.last_pos[1]
        diffz = tz - self.last_pos[2]
        time_diff = (current_time - self.last_time) / 1000

        velocity = (diffx / time_diff, diffy / time_diff, diffz / time_diff)
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
        translation = ZedPipeDataTranslation(x=tx, y=ty, z=tz)

        return ZedPipeData(
            rotation=rotation,
            translation=translation,
            velocity=velocity,
            tracker_confidence=self.zed_pose.pose_confidence,
        )
