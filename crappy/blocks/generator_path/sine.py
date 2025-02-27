# coding: utf-8

from time import time
from numpy import sin, pi
from typing import Union, Dict

from .path import Path, condition_type


class Sine(Path):
  """This path generates a sine wave varying with time until the stop condition
  is met."""

  def __init__(self,
               _last_time: float,
               _last_cmd: float,
               condition: Union[str, condition_type],
               freq: float,
               amplitude: float,
               offset: float = 0,
               phase: float = 0) -> None:
    """Sets the args and initializes the parent class.

    Args:
      _last_time: The last timestamp when a command was generated. For internal
        use only, do not overwrite.
      _last_cmd: The last sent command. For internal use only, do not
        overwrite.
      condition: The condition for switching to the next path. Refer to
        :ref:`generator path` for more info.
      freq: The frequency of the sine in `Hz`.
      amplitude: The amplitude of the sine wave (peak to peak).
      offset: The offset of the sine (average value).
      phase: The phase of the sine (in radians).
    """

    Path.__init__(self, _last_time, _last_cmd)

    # Setting the attributes
    self._condition = self.parse_condition(condition)
    self._amplitude = amplitude / 2
    self._offset = offset
    self._phase = phase
    self._k = 2 * pi * freq

  def get_cmd(self, data: Dict[str, list]) -> float:
    """Returns the value to send or raises :exc:`StopIteration` if the stop
    condition is met."""

    # Checking if the stop condition is met
    if self._condition(data):
      raise StopIteration

    # Returning the current signal value
    return sin((time() - self.t0) * self._k - self._phase) * \
        self._amplitude + self._offset
