import subprocess
from typing import Dict

import pyrealsense2 as rs
from loguru import logger


class T265(object):
    """
    Realsense T265 Tracking Camera interface. Manages pulling data off of the camera for use by the transforms to get it in the correct reference frame.
    """

    def __init__(self):
        self.pipe = None

    def get_rs_devices(self) -> Dict:
        """Get Serial numbers of connected RealSense devices"""
        rs_devices = {}
        rs_context: rs.context = rs.context()
        for i in range(len(rs_context.devices)):
            rs_device = rs_context.devices[i]
            rs_device_name = rs_device.get_info(rs.camera_info.name)
            rs_device_sid = rs_device.get_info(rs.camera_info.serial_number)
            if "T265" in rs_device_name:
                rs_devices["T265"] = rs_device_sid
            elif "D435I" in rs_device_name:
                rs_devices["D435I"] = rs_device_sid

        return rs_devices

    def setup(self) -> None:
        try:
            # Reference to a post showing how to use multiple camera: https://github.com/IntelRealSense/librealsense/issues/1735
            logger.debug("Obtaining connected RealSense devices...")

            # very ancedotally, running this before trying to open the connection seems to help
            subprocess.run(["rs-enumerate-devices"], check=True)

            rs_devices = self.get_rs_devices()

            logger.debug("Obtaining T265 connection ID...")
            t265_sid = rs_devices.get("T265", 0)
            if t265_sid == 0:
                raise ValueError("RealSense T265 not connected. Please connect & retry")

            logger.debug("Creating RealSense context")
            context = rs.context()

            logger.debug("Creating RealSense pipeline")
            self.pipe: rs.pipeline = rs.pipeline()
            logger.debug("Creating T265 config")
            t265_config = rs.config()

            logger.debug("Enabling T265 device")
            t265_config.enable_device(t265_sid)
            logger.debug("Enabling T265 stream")
            t265_config.enable_stream(rs.stream.pose)
            logger.debug("Starting RealSense pipeline")
            self.pipe.start(t265_config)
            logger.debug("T265 fully connected")

        except Exception as e:
            logger.exception(f"T265: Error connecting to Realsense Camera: {e}")
            raise e

    def get_pipe_data(self) -> rs.pose:
        # Wait for the next set of frames from the camera
        frames = self.pipe.wait_for_frames()

        # # Fetch pose frame
        pose = frames.get_pose_frame()

        if pose:  # is not None
            return pose.get_pose_data()

    def stop(self) -> None:
        try:
            logger.debug("Closing RealSense pipeline")
            self.pipe.stop()
        except:
            logger.exception("Couldn't stop the pipe")
