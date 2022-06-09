import time
from typing import Optional, Tuple

import cv2
from loguru import logger
from bell.vrc.utils.decorators import run_forever

class CaptureDevice:
    def __init__(
        self,
        protocol: str,
        video_device: str,
        res: Tuple[int, int],
        framerate: Optional[int] = None,
    ):
        self.protocol = protocol
        self.dev = video_device
        self.res = res

        # "gst-launch-1.0 nvarguscamerasrc ! 'video/x-raw(memory:NVMM),width=1920,height=1080,framerate=30/1,format=NV12' ! nvv4l2h265enc bitrate=10000000 iframeinterval=40 ! video/x-h265, stream-format=byte-stream ! rndbuffersize min=1500 max=1500 ! tee name=t ! queue ! udpsink host=192.168.1.140 port=5000 t. ! queue ! udpsink host=192.168.1.112 port=5000"
        # "gst-launch-1.0 nvarguscamerasrc ! 'video/x-raw(memory:NVMM),width=1920,height=1080,framerate=30/1,format=NV12' ! videoconvert ! nvoverlaysink"

        if self.protocol == "v4l2":
            # if the framerate argument is supplied, we will modify the connection
            # string to provide a rate limiter to the incoming string at virtually
            # no performance penalty
            if framerate is None:
                frame_string = "video/x-raw,format=BGRx"
            else:
                frame_string = (
                    f"videorate ! video/x-raw,format=BGRx,framerate={framerate}/1"
                )

            # this is the efficient way of capturing, leveraging the hardware
            # JPEG decoder on the jetson
            connection_string = f"v4l2src device={video_device} io-mode=2 ! image/jpeg,width=1280,height=720,framerate=60/1 ! jpegparse ! nvv4l2decoder mjpeg=1 ! nvvidconv ! {frame_string} ! videoconvert ! video/x-raw,width={res[0]},height={res[1]},format=BGRx ! appsink"

        elif self.protocol == "argus":
            if framerate is None:
                frame_string = "video/x-raw,format=BGR"
            else:
                frame_string = (
                    f"videorate ! video/x-raw,format=BGR,framerate={framerate}/1"
                )

            connection_string = f"nvarguscamerasrc ! video/x-raw(memory:NVMM), width=1280, height=720,format=NV12, framerate=60/1 ! nvvidconv ! video/x-raw,format=BGRx ! videoconvert ! {frame_string},width={res[0]},height={res[1]} ! appsink"

        else:
            raise ValueError

        # this is the inefficient way of capturing, using the software decoder running on CPU
        # self.cv = cv2.VideoCapture("v4l2src device=/dev/video2 io-mode=2 ! image/jpeg,width=1280,height=720,framerate=60/1 ! jpegparse ! jpegdec ! videoconvert ! appsink sync=false")

        # this is how we might have to capture from csi cameras..
        # self.cv = cv2.VideoCapture("nvarguscamerasrc ! 'video/x-raw(memory:NVMM), width=1920, height=1080, framerate=30/1, format=NV12' ! videoconvert ! appsink sync=false",)

        # create the gstreamer pipeline
        self.cv = cv2.VideoCapture(connection_string)

    def read(self) -> Tuple[bool, Optional[cv2.Mat]]:
        return self.cv.read()

    def read_gray(self) -> Tuple[bool, Optional[cv2.Mat]]:
        ret, img = self.cv.read()
        if ret:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return ret, img

    @run_forever(frequency=100)
    def run(self) -> None:
        # try to read frame
        ret, _ = self.read()

        if not ret:
            logger.warning("cv2.VideoCapture read failed")


if __name__ == "__main__":
    cam = CaptureDevice(
        protocol="argus", video_device="/dev/video0", res=(1280, 720), framerate=30
    )
    cam.run()
