# coding: utf-8

import numpy as np
from time import time
from typing import List, Optional
from dataclasses import dataclass

from .inout import InOut
from .._global import OptionalModule
try:
  import PyDAQmx
except (ModuleNotFoundError, ImportError):
  PyDAQmx = OptionalModule("PyDAQmx")


@dataclass
class _Channel:
  """This class is a simple structure holding all the attributes a DAQmx
  channel can have."""

  name: str
  range_num: float = 5
  gain: float = 1
  offset: float = 0
  make_zero: bool = False


class Daqmx(InOut):
  """"""

  def __init__(self,
               device: str = 'Dev1',
               channels: Optional[List[str]] = None,
               gain: Optional[List[float]] = None,
               offset: Optional[List[float]] = None,
               ranges: Optional[List[float]] = None,
               make_zero: Optional[List[bool]] = True,
               sample_rate: float = 10000,
               out_channels: Optional[List[str]] = None,
               out_gain: Optional[List[float]] = None,
               out_offset: Optional[List[float]] = None,
               out_ranges: Optional[List[float]] = None) -> None:
    """Sets the args and initializes the parent class.

    Args:
      device: The name of the device to open, as a :obj:`str`.
      channels: A :obj:`list` containing the names of the channels to use as
        inputs, given as :obj:`str`. Typical names for inputs are ``'aiX'```,
        with `X` an integer.
      gain: A :obj:`list` containing for each input channel the gain to apply
        to the measured voltage, as a :obj:`float`. The returned voltage is
        calculated as follows :
        ::

          returned_voltage = gain * measured_voltage + offset

        If not given, no gain is applied to the measured values.
      offset: A :obj:`list` containing for each input channel the offset to
        apply to the measured voltage, as a :obj:`float`. The returned voltage
        is calculated as follows :
        ::

          returned_voltage = gain * measured_voltage + offset

        If not given, no offset is applied to the measured values.
      ranges: A :obj:`list` containing for each input channel the range to set
        for that channel, as an :obj:`float`. The possible range values are :
        ::

          0.5, 1., 2.5, 5.

        If not given, all input channels will be set to the range `5`.
      make_zero: A :obj:`list` containing for each input channel a :obj:`bool`
        indicating whether the channel should be zeroed or not. If so, data
        will be acquired on this channel before the test starts, and a
        compensation value will be deduced so that the offset of this channel
        is `0`. **It will only take effect if the ``make_zero_delay`` argument
        of the :ref:`IOBlock` controlling the Comedi is set** ! If not given,
        the channels are by default not zeroed.
      sample_rate: The frequency of the acquisition, as a :obj:`float`. The
        higher this number, the more noise there is on the signal but the
        higher the acquisition frequency.
      out_channels: A :obj:`list` containing the names of the channels to use
        as outputs, given as :obj:`str`. Typical names for outputs are
        ``'aoX'``, with `X` an integer.
      out_gain: A :obj:`list` containing for each output channel the gain to
        apply to the command voltage, as a :obj:`float`. The set voltage is
        calculated as follows :
        ::

          set_voltage = out_gain * command_voltage + out_offset

        If not given, no gain is applied to the command values.
      out_offset: A :obj:`list` containing for each output channel the offset
        to apply to the command voltage, as a :obj:`float`. The set voltage is
        calculated as follows :
        ::

          set_voltage = out_gain * command_voltage + out_offset

        If not given, no offset is applied to the command values.
      out_ranges: A :obj:`list` containing for each output channel the range to
        set for that channel, as an :obj:`float`. The possible range values
        are :
        ::

          0.5, 1., 2.5, 5.

        If not given, all output channels will be set to the range `5`.

    Note:
      All the :obj:`list` given as arguments for the input channels should have
      the same length, and same for the output channels. If that's not the
      case, all the given lists are treated as if they had the same length
      as the shortest given list.
    """

    super().__init__()

    self._device = device
    self._sample_rate = sample_rate

    # Setting the defaults for arguments that are not given
    if channels is None:
      channels = list()
    if out_channels is None:
      channels = list()

    if ranges is None:
      ranges = [5 for _ in channels]
    if gain is None:
      gain = [1 for _ in channels]
    if offset is None:
      offset = [0 for _ in channels]
    if make_zero is None:
      make_zero = [False for _ in channels]

    if out_ranges is None:
      out_ranges = [5 for _ in out_channels]
    if out_gain is None:
      out_gain = [1 for _ in out_channels]
    if out_offset is None:
      out_offset = [0 for _ in out_channels]

      # Creating the channel objects
      self._channels = [_Channel(name=chan, range_num=r_num, gain=g,
                                 offset=off, make_zero=make_z)
                        for chan, r_num, g, off, make_z in
                        zip(channels, ranges, gain, offset, make_zero)]

      self._out_channels = [_Channel(name=chan, range_num=r_num, gain=g,
                                     offset=off) for chan, r_num, g, off in
                            zip(out_channels, out_ranges,
                                out_gain, out_offset)]

    self._handle, self._out_handle = None, None
    self._n_reads = PyDAQmx.int32()

  def open(self) -> None:
    """Opens the device and initializes the input and output channels."""

    PyDAQmx.DAQmxResetDevice(self._device)

    if self._channels:
      # Opening the device for reading
      self._handle = PyDAQmx.TaskHandle()
      PyDAQmx.DAQmxCreateTask('', PyDAQmx.byref(self._handle))

      # Setting up the input channels
      for chan in self._channels:
        PyDAQmx.DAQmxCreateAIVoltageChan(self._handle,
                                         f"{self._device}/{chan.name}", '',
                                         PyDAQmx.DAQmx_Val_Cfg_Default, 0,
                                         chan.range_num,
                                         PyDAQmx.DAQmx_Val_Volts, None)

    if self._out_channels:
      # Opening the device for writing
      self._out_handle = PyDAQmx.TaskHandle()
      PyDAQmx.DAQmxCreateTask('', PyDAQmx.byref(self._out_handle))

      # Setting up the output channels
      for chan in self._out_channels:
        PyDAQmx.DAQmxCreateAOVoltageChan(self._out_handle, 
                                         f"{self._device}/{chan.name}", '', 0, 
                                         chan.range_num, 
                                         PyDAQmx.DAQmx_Val_Volts, None)
        PyDAQmx.DAQmxStartTask(self._out_handle)
  
  def make_zero(self, delay: float) -> None:
    """Overriding of the method of the parent class, because the user can
    choose which channels should be zeroed or not.

    It simply performs the regular zeroing, and resets the compensation to
    zero for the channels that shouldn't be zeroed.
    """

    # No need to acquire data if no channel should be zeroed
    if any(chan.make_zero for chan in self._channels):

      # Acquiring the data
      super().make_zero(delay)

      # Proceed only if the acquisition went fine
      if self._compensations:
        # Resetting the compensation for channels that shouldn't be zeroed
        self._compensations = [comp if chan.make_zero else 0 for comp, chan
                               in zip(self._compensations, self._channels)]
  
  def get_data(self) -> List[float]:
    """Creates and starts an acquisition task, and returns the acquired
    values."""

    # Defining the acquisition task and the buffer, and starting it
    PyDAQmx.DAQmxCfgSampClkTiming(self._handle, '', self._sample_rate,
                                  PyDAQmx.DAQmx_Val_Rising,
                                  PyDAQmx.DAQmx_Val_FiniteSamps,
                                  2)
    PyDAQmx.DAQmxStartTask(self._handle)
    data = np.empty((len(self._channels), 1), dtype=np.float64)

    # Reading the acquired values and stopping the task
    t0 = time()
    PyDAQmx.DAQmxReadAnalogF64(self._handle, 1, 10.0,
                               PyDAQmx.DAQmx_Val_GroupByChannel, data,
                               len(self._channels),
                               PyDAQmx.byref(self._n_reads), None)
    PyDAQmx.DAQmxStopTask(self._handle)

    return [t0] + [data[i, :] * chan.gain + chan.offset
                   for i, chan in enumerate(self._channels)]

  def set_cmd(self, *cmd: float) -> None:
    """Sets the command value on the output channels.

    There should be as many commands as there are output channels. In case the
    numbers of channels and commands don't match, an exception is raised.
    """

    # Applying the gains and offsets to the commands
    out_gains = [chan.gain for chan in self._out_channels]
    out_offsets = [chan.offset for chan in self._out_channels]
    data = np.array(cmd, dtype=np.float64) * out_gains + out_offsets

    # Setting the commands
    PyDAQmx.DAQmxWriteAnalogF64(self._out_handle, 1, 1, 10.0,
                                PyDAQmx.DAQmx_Val_GroupByChannel,
                                data, None, None)

  def close(self) -> None:
    """Closes the processes of the input and output channels."""

    # Stopping and closing the processes for data acquisition
    if self._handle is not None:
      PyDAQmx.DAQmxStopTask(self._handle)
      PyDAQmx.DAQmxClearTask(self._handle)

    # Stopping and closing the processes for writing data
    if self._out_handle is not None:
      PyDAQmx.DAQmxStopTask(self._out_handle)
      PyDAQmx.DAQmxClearTask(self._out_handle)
