# coding: utf-8

from time import time
from typing import Tuple, Optional
from numpy import ndarray
from .camera import Camera
from .._global import OptionalModule

try:
  import cv2
except (ModuleNotFoundError, ImportError):
  cv2 = OptionalModule("opencv-python")


class Webcam(Camera):
  """A basic class for reading images from a USB camera (including webcams).

  It relies on the OpenCv library. Note that it was purposely kept extremely
  simple as it is mainly used as a demo. See :ref:`Camera OpenCV` and
  :ref:`Camera GStreamer` for classes giving a finer control over the device.
  """

  def __init__(self) -> None:
    """Sets variables and adds the channels setting."""

    super().__init__()
    self.name = "webcam"
    self._cap = None
    self.add_choice_setting(name="channels",
                            choices=('1', '3'),
                            default='1')

  def open(self, device_num: Optional[int] = 0, **kwargs) -> None:
    """Opens the video stream and sets any user-specified settings.

    Args:
      device_num (:obj:`int`, optional): The number of the device to open.
      **kwargs: Any additional setting to set before opening the graphical
        interface.
    """

    # Opening the videocapture device
    self._cap = cv2.VideoCapture(device_num)

    # Setting the kwargs if any
    self.set_all(**kwargs)

  def get_image(self) -> Tuple[float, ndarray]:
    """Grabs a frame from the videocapture object and returns it along with a
    timestamp."""

    # Grabbing the frame and the timestamp
    t = time()
    ret, frame = self._cap.read()

    # Checking the integrity of the frame
    if not ret:
      raise IOError("Error reading the camera")

    # Returning the image in the right format, and its timestamp
    if self.channels == '1':
      return t, cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    else:
      return t, frame

  def close(self) -> None:
    """Releases the videocapture object."""

    if self._cap is not None:
      self._cap.release()
