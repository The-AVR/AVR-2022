import multiprocessing
import time
from typing import List, Optional, Tuple

import numpy as np
from bell.vrc.utils.decorators import try_except
from capture_device import CaptureDevice
from loguru import logger
from pupil_apriltags import Detection, Detector


class AprilTagWrapper:
    def __init__(
        self, camera_params: Tuple[float, float, float, float], tag_size: float
    ):
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

    def process_image(self, frame: np.uint8) -> List[Detection]:
        """
        Takes an image as input and returns the detected apriltags in list format
        """
        return self.detector.detect(
            frame,
            estimate_tag_pose=True,
            camera_params=self.camera_params,
            tag_size=self.tag_size,
        )


class AprilTagVPS:
    def __init__(
        self,
        protocol: str,
        video_device: str,
        res: Tuple[int, int],
        camera_params: Tuple[float, float, float, float],
        tag_size: float,
        framerate: Optional[int] = None,
    ):
        # camera parameters
        self.protocol = protocol
        self.video_device = video_device
        self.res = res
        self.framerate = framerate

        # pupil april tags wrapper
        self.atag = AprilTagWrapper(camera_params=camera_params, tag_size=tag_size)

        # setup processing queue
        self.img_queue = multiprocessing.Queue()
        self.tags_queue = multiprocessing.Queue()

        self.tags = None
        self.tags_timestamp = time.time()

        # record average framerate
        self.avg = 0.0
        # record number of images processed
        self.num_images = 0

    def run(self) -> None:
        # sourcery skip: use-named-expression
        """
        Kicks off the AprilTagVPS pipeline, capturing images from
        a v4l2 camera @ 'video_device' and uses 'camera_params' along with
        'tag_size' to calculate pose.
        """
        # we will setup 2 processing consumers for the imagery.
        for i in range(2):
            proc = multiprocessing.Process(
                target=self.perception_loop, args=[], daemon=True  # type: ignore
            )
            proc.start()

        # start the capturing process
        proc = multiprocessing.Process(target=self.capture_loop, args=(), daemon=True)
        proc.start()

        last_loop = time.time()
        delta_buckets = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        i = 0

        while True:
            # if the perception loop has completed analysis on a frame,
            # show some stats or even render the frame
            if self.tags_queue.empty():
                time.sleep(0.01)
                continue

            self.num_images += 1
            now = time.time()

            # try to get a tag from the queue
            tags = self.tags_queue.get()
            if tags:
                self.tags = tags
                self.tags_timestamp = now
            else:
                self.tags = []

            # calculate the framerate
            tdelta = now - last_loop
            delta_buckets[i % 10] = tdelta  # type: ignore
            self.avg = 1 / (sum(delta_buckets) / 10)
            last_loop = now
            i += 1

    def capture_loop(self) -> None:
        """
        Captures frames from the camera and places them into the image queue
        to be consumed downstream by "perception loop". Checks to make sure queue
        is not being overloaded and limits queue size to "max_depth".
        """
        max_depth = 3
        capture = CaptureDevice(
            self.protocol, self.video_device, self.res, self.framerate
        )

        logger.success("Capture loop started!")

        while True:
            ret, img = capture.read_gray()

            # if theres room in the queue and we have a valid image
            if (self.img_queue.qsize() < max_depth) and (ret is True):
                # put the image in the queue
                self.img_queue.put(img)

            time.sleep(0.01)

    @try_except(reraise=True)
    def perception_loop(self) -> None:
        """
        Pulls images off the image queue, hands them to the apriltag detector,
        and then places the results in the tags queue.
        """
        logger.success("Perception loop started!")

        while True:
            if not self.img_queue.empty():
                img = self.img_queue.get()
                tags = self.atag.process_image(img)
                self.tags_queue.put(tags)
            else:
                time.sleep(0.01)


if __name__ == "__main__":
    at = AprilTagVPS(
        protocol="argus",
        video_device="/dev/video0",
        res=(1280, 720),
        camera_params=(584.3866, 583.3444, 661.2944, 320.7182),
        tag_size=0.174,  # full size tag
        # old comment had 0.057
        framerate=None,
    )

    at.run()
