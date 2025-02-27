# coding: utf-8

from time import time, strftime, gmtime
from typing import Tuple, Optional, Dict, Any
import numpy as np
from .camera import Camera


class Fake_camera(Camera):
  """This camera class generates images without requiring any actual camera or
  existing image file.

  The generated images are just a gradient of grey levels, with a line moving
  as a function of time. It is possible to tune the dimension of the image, the
  frame rate and the speed of the line.
  """

  def __init__(self) -> None:
    """Initializes the parent class and instantiates the settings."""

    super().__init__()
    self._frame_nr = -1

    self.add_scale_setting('width', 1, 4096, None, self._gen_image, 1280)
    self.add_scale_setting('height', 1, 4096, None, self._gen_image, 1024)
    self.add_scale_setting('speed', 0., 800., None, None, 100.)
    self.add_scale_setting('fps', 0.1, 100., None, None, 50.)

  def open(self, **kwargs) -> None:
    """Sets the settings, generates the first image and initializes the time
    counter."""

    self.set_all(**kwargs)

    self._gen_image()

    self._t0 = time()
    self._t = self._t0

  def get_image(self) -> Tuple[Dict[str, Any], np.ndarray]:
    """Returns the updated image, depending only on the current timestamp.

    Also includes a waiting loop in order to achieve the right frame rate.
    """

    # Waiting in order to achieve the right frame rate
    while time() - self._t < 1 / self.fps:
      pass

    self._t = time()
    self._frame_nr += 1

    # Splitting the image to make a moving line
    row = int(self.speed * (self._t - self._t0)) % self.height
    metadata = {'t(s)': self._t,
                'DateTimeOriginal': strftime("%Y:%m:%d %H:%M:%S",
                                             gmtime(self._t)),
                'SubsecTimeOriginal': f'{self._t % 1:.6f}',
                'ImageUniqueID': self._frame_nr}
    return metadata, np.concatenate((self._img[row:], self._img[:row]), axis=0)

  def _gen_image(self, _: Optional[float] = None) -> None:
    """Generates the base gradient image, that will be splitted and returned
    in the :meth:`get_image` method"""

    self._img = np.arange(self.height) * 255. / self.height
    self._img = np.repeat(self._img.reshape(self.height, 1),
                          self.width, axis=1).astype(np.uint8)
