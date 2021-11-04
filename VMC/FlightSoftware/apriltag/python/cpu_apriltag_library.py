# python standard libraries
import logging
import time
import multiprocessing
import os

# pip installed packages
import numpy
from setproctitle import setproctitle
from colored import fore, back, style
from pupil_apriltags import Detector

from loguru import logger

from capture_device import CaptureDevice


# camera_params=[584.3866,583.3444,661.2944,320.7182],tag_size=0.057


class AprilTagWrapper(object):
    def __init__(self, camera_params, tag_size):
        self.camera_params = camera_params
        self.tag_size = tag_size

        self.detector = Detector(
            families="tag36h11",
            nthreads=2,
            quad_decimate=1.5,
            quad_sigma=0.0,
            refine_edges=1,
            decode_sharpening=0.25,
            debug=0,
        )

    def process_image(self, frame):
        """
        Takes an image as input and returns the detected apriltags in list format
        """
        tags = self.detector.detect(
            frame,
            estimate_tag_pose=True,
            camera_params=self.camera_params,
            tag_size=self.tag_size,
        )
        return tags


class AprilTagVPS(object):
    def __init__(
        self,
        protocol,
        video_device,
        res,
        camera_params,
        tag_size,
        framerate=None,
    ):
        self.protocol = protocol
        self.video_device = video_device
        self.res = res[0:2]
        self.framerate = framerate

        self.atag = AprilTagWrapper(camera_params=camera_params, tag_size=tag_size)

        self.img_queue = multiprocessing.Queue()
        self.tags_queue = multiprocessing.Queue()

        self.tags = None
        self.tags_timestamp = time.time()

        self.avg = 0.0
        self.num_images = 0

    def start(self):
        """
        Kicks off the AprilTagVPS pipeline, capturing images from a v4l2 camera @ 'video_device' and uses 'camera_params' along with 'tag_size' to calculate pose.
        """
        self.consumer_processes = []
        # we will setup 2 processing consumers for the imagery.
        for i in range(0, 2):
            proc = multiprocessing.Process(
                target=self.perception_loop, args=[], daemon=True  # type: ignore
            )
            proc.start()

        # start the capturing process
        proc = multiprocessing.Process(target=self.capture_loop, args=[], daemon=True)  # type: ignore
        proc.start()

        last_loop = time.time()
        delta_buckets = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        i = 0

        while True:
            # if the perception loop has completed analysis on a frame, show some stats or even render the frame
            if not self.tags_queue.empty():
                self.num_images += 1
                now = time.time()
                tags = self.tags_queue.get()
                if tags:
                    self.tags = tags
                    self.tags_timestamp = now
                else:
                    self.tags = []

                tdelta = now - last_loop
                delta_buckets[i % 10] = tdelta  # type: ignore
                self.avg = 1 / (sum(delta_buckets) / 10)
                # logger.debug(f"{fore.GREEN}AT: FPS {avg:04.1f} \t Tags: {len(tags)}")  # type: ignore
                last_loop = now
                i = i + 1
            else:
                time.sleep(0.01)

    def capture_loop(self):
        """
        Captures frames from the camera and places them into the image queue to be consumed downstream by "perception loop"
        Checks to make sure queue is not being overloaded and limits queue size to "max_depth"
        """
        setproctitle("AprilTagVPS_capture")
        max_depth = 3
        capture = CaptureDevice(
            self.protocol, self.video_device, self.res, self.framerate
        )
        logger.debug(f"{fore.GREEN}AT: Capture Loop Started!{style.RESET}")  # type: ignore
        while True:
            ret, img = capture.read_gray()
            # logger.debug(f"{fore.GREEN}AT: ret: {ret}{style.RESET}") #type: ignore
            # if theres room in the queue and we have a valid image
            if (self.img_queue.qsize() < max_depth) and (ret is True):
                # put the image in the queue
                self.img_queue.put(img)
                # logger.debug(f"{fore.GREEN}AT: Placed an image!{style.RESET}") #type: ignore
            time.sleep(0.01)

    def perception_loop(self):
        """
        Pulls images off the image queue, hands them to the apriltag detector, and then places the results in the tags queue
        """
        setproctitle("AprilTagVPS_perception")
        logger.debug(f"{fore.GREEN}AT: Perception Loop Started!{style.RESET}")  # type: ignore
        try:
            while True:
                if not self.img_queue.empty():
                    img = self.img_queue.get()
                    tags = self.atag.process_image(img)
                    self.tags_queue.put(tags)
                else:
                    time.sleep(0.01)
        except Exception as e:
            logger.exception(f"{fore.RED}AT: Perception Loop Error: {e}{style.RESET}")  # type: ignore
            raise e


if __name__ == "__main__":
    at = AprilTagVPS(
        protocol="argus",
        video_device="/dev/video0",
        res=[1280, 720],
        camera_params=[584.3866, 583.3444, 661.2944, 320.7182],
        tag_size=0.174,  # full size tag
        framerate=None,
    )

    at.start()

"""
gst-launch-1.0 nvarguscamerasrc sensor_id=0 ! videoconvert ! videorate ! 'video/x-raw(memory:NVMM),framerate=10/1' ! nvv4l2h264enc maxperf-enable=1 preset-level=1 bitrate=5000000 ! rtph264pay config-interval=1 pt=96 ! udpsink host=192.168.1.185 port=5000
"""
