# coding: utf-8

from time import time, sleep
from typing import Union, Optional, List
from .inout import InOut
from ..tool import ft232h_server as ft232h, Usb_server
from .._global import OptionalModule

try:
  import smbus2
except (ModuleNotFoundError, ImportError):
  smbus2 = OptionalModule("smbus2")

try:
  import RPi.GPIO as GPIO
except (ModuleNotFoundError, ImportError):
  GPIO = OptionalModule("RPi.GPIO")

# Register Map
NAU7802_Scale_Registers = {'PU_CTRL': 0x00,
                           'CTRL1': 0x01,
                           'CTRL2': 0x02,
                           'OCAL1_B2': 0x03,
                           'OCAL1_B1': 0x04,
                           'OCAL1_B0': 0x05,
                           'GCAL1_B3': 0x06,
                           'GCAL1_B2': 0x07,
                           'GCAL1_B1': 0x08,
                           'GCAL1_B0': 0x09,
                           'OCAL2_B2': 0x0A,
                           'OCAL2_B1': 0x0B,
                           'OCAL2_B0': 0x0C,
                           'GCAL2_B3': 0x0D,
                           'GCAL2_B2': 0x0E,
                           'GCAL2_B1': 0x0F,
                           'GCAL2_B0': 0x10,
                           'I2C_CONTROL': 0x11,
                           'ADCO_B2': 0x12,
                           'ADCO_B1': 0x13,
                           'ADCO_B0': 0x14,
                           'ADC': 0x15,
                           'OTP_B1': 0x16,
                           'OTP_B0': 0x17,
                           'PGA': 0x1B,
                           'PGA_PWR': 0x1C,
                           'DEVICE_REV': 0x1F}

# Bits within the PU_CTRL register
NAU7802_PU_CTRL_Bits = {'PU_CTRL_RR': 0,
                        'PU_CTRL_PUD': 1,
                        'PU_CTRL_PUA': 2,
                        'PU_CTRL_PUR': 3,
                        'PU_CTRL_CS': 4,
                        'PU_CTRL_CR': 5,
                        'PU_CTRL_OSCS': 6,
                        'PU_CTRL_AVDDS': 7}

# Bits within the CTRL2 register
NAU7802_CTRL2_Bits = {'CTRL2_CALMOD': 0,
                      'CTRL2_CALS': 2,
                      'CTRL2_CAL_ERROR': 3,
                      'CTRL2_CRS': 4,
                      'CTRL2_CHS': 7}

# Bits within the PGA PWR register
NAU7802_PGA_PWR_Bits = {'PGA_PWR_PGA_CURR': 0,
                        'PGA_PWR_ADC_CURR': 2,
                        'PGA_PWR_MSTR_BIAS_CURR': 4,
                        'PGA_PWR_PGA_CAP_EN': 7}

# Allowed Low drop out regulator voltages
NAU7802_LDO_Values = {2.4: 0b111,
                      2.7: 0b110,
                      3.0: 0b101,
                      3.3: 0b100,
                      3.6: 0b011,
                      3.9: 0b010,
                      4.2: 0b001,
                      4.5: 0b000}

# Allowed gains
NAU7802_Gain_Values = {1: 0b000,
                       2: 0b001,
                       4: 0b010,
                       8: 0b011,
                       16: 0b100,
                       32: 0b101,
                       64: 0b110,
                       128: 0b111}

# Allowed samples per second
NAU7802_SPS_Values = {10: 0b000,
                      20: 0b001,
                      40: 0b010,
                      80: 0b011,
                      320: 0b111}

# Calibration state
NAU7802_Cal_Status = {'CAL_SUCCESS': 0,
                      'CAL_IN_PROGRESS': 1,
                      'CAL_FAILURE': 2}

NAU7802_Backends = ['Pi4', 'ft232h']

NAU7802_VREF = 3.3


class Nau7802(Usb_server, InOut):
  """Class for controlling Sparkfun's NAU7802 load cell conditioner.

  The Nau7802 InOut block is meant for reading output values from a NAU7802
  load cell conditioner, using the I2C protocol. The output is in Volts by
  default, but can be converted to Newtons using ``gain`` and ``offset``.
  """

  def __init__(self,
               backend: str,
               i2c_port: int = 1,
               device_address: int = 0x2A,
               gain_hardware: int = 128,
               sample_rate: int = 80,
               int_pin: Optional[Union[str, int]] = None,
               gain: float = 1,
               offset: float = 0,
               ft232h_ser_num: Optional[str] = None) -> None:
    """Checks the validity of the arguments..

    Args:
      backend (:obj:`str`): The backend for communicating with the NAU7802.
        Should be one of:
        ::

          'Pi4', 'ft232h'

        to use the device from a Raspberry Pi or from a PC through an FT232H
        USB to I2C converter, respectively. See :ref:`Crappy for embedded
        hardware` for details.
      i2c_port (:obj:`int`, optional): The I2C port over which the NAU7802
        should communicate. On most Raspberry Pi models the default I2C port is
        `1`.
      device_address (:obj:`int`, optional): The I2C address of the NAU7802. It
        is impossible to change this address, so it is not possible to have
        several NAU7802 on the same i2c bus.
      gain_hardware (:obj:`int`, optional): The gain to be used by the
        programmable gain amplifier. Setting a high gain allows reading small
        voltages with a better precision, but it might saturate the sensor for
        higher voltages. Available gains are:
        ::

          1, 2, 4, 8, 16, 32, 64, 128

      sample_rate (:obj:`int`, optional): The sample rate for data conversion.
        The higher the rate, the greater the noise. Available sample rates are:
        ::

          10, 20, 40, 80, 320

      int_pin (:obj:`int` or :obj:`str`, optional): Optionally, reads the end
        of conversion signal from a GPIO rather than from an I2C message.
        Speeds up the reading and decreases the traffic on the bus, but
        requires one extra wire. With the backend `'Pi4'`, give the index of
        the GPIO in BCM convention. With the `'ft232h'` backend, give the name
        of the GPIO in the format `Dx` or `Cx`.
      gain (:obj:`float`, optional): Allows to tune the output value according
        to the formula:
        ::

          output = gain * tension + offset.

      offset (:obj:`float`, optional): Allows to tune the output value
        according to the formula:
        ::

          output = gain * tension + offset.

      ft232h_ser_num (:obj:`str`, optional): If backend is `'ft232h'`, the
        serial number of the ft232h to use for communication.
    """

    if backend not in NAU7802_Backends:
      raise ValueError("backend should be in {}".format(NAU7802_Backends))

    Usb_server.__init__(self,
                        serial_nr=ft232h_ser_num if ft232h_ser_num else '',
                        backend=backend)
    InOut.__init__(self)
    current_file, block_number, command_file, answer_file, block_lock, \
        current_lock = super().start_server()

    if backend == 'Pi4':
      self._bus = smbus2.SMBus(i2c_port)
    else:
      self._bus = ft232h(mode='I2C',
                         block_number=block_number,
                         current_file=current_file,
                         command_file=command_file,
                         answer_file=answer_file,
                         block_lock=block_lock,
                         current_lock=current_lock,
                         serial_nr=ft232h_ser_num)
    self._device_address = device_address
    self._backend = backend

    if gain_hardware not in NAU7802_Gain_Values:
      raise ValueError("gain_hardware should be in {}".format(list(
        NAU7802_Gain_Values.keys())))
    else:
      self._gain_hardware = gain_hardware

    if sample_rate not in NAU7802_SPS_Values:
      raise ValueError("sample_rate should be in {}".format(list(
        NAU7802_SPS_Values.keys())))
    else:
      self._sample_rate = sample_rate

    if int_pin is not None:
      if backend == 'ft232h' and not isinstance(int_pin, str):
        raise TypeError('int_pin should be a string when using the ft232h '
                        'backend !')
      elif backend == 'Pi4' and not isinstance(int_pin, int):
        raise TypeError('int_pin should be an int when using the Pi4 '
                        'backend !')
    self._int_pin = int_pin

    self._gain = gain
    self._offset = offset

  def open(self) -> None:
    """Sets the I2C communication and device."""

    if not self._is_connected():
      raise IOError("The NAU7802 is not connected")

    # Resetting the device
    self._set_bit(NAU7802_PU_CTRL_Bits['PU_CTRL_RR'],
                  NAU7802_Scale_Registers['PU_CTRL'], 1)
    sleep(0.001)
    self._set_bit(NAU7802_PU_CTRL_Bits['PU_CTRL_RR'],
                  NAU7802_Scale_Registers['PU_CTRL'], 0)

    # Powering up the device - takes approx 200µs
    self._set_bit(NAU7802_PU_CTRL_Bits['PU_CTRL_PUD'],
                  NAU7802_Scale_Registers['PU_CTRL'], 1)
    self._set_bit(NAU7802_PU_CTRL_Bits['PU_CTRL_PUA'],
                  NAU7802_Scale_Registers['PU_CTRL'], 1)

    t0 = time()
    while not self._get_bit(NAU7802_PU_CTRL_Bits['PU_CTRL_PUR'],
                            NAU7802_Scale_Registers['PU_CTRL']):
      if time() - t0 > 0.1:
        raise TimeoutError("Waited too long for the device to power up !")

    # Setting the Low Drop Out voltage to 3.3V and setting the gain
    value = NAU7802_Gain_Values[self._gain_hardware]
    self._bus.write_byte_data(self._device_address,
                              NAU7802_Scale_Registers['CTRL1'], value)
    self._set_bit(NAU7802_PU_CTRL_Bits['PU_CTRL_AVDDS'],
                  NAU7802_Scale_Registers['PU_CTRL'], 1)

    # Setting the sample rate
    self._bus.write_byte_data(self._device_address,
                              NAU7802_Scale_Registers['CTRL2'],
                              NAU7802_SPS_Values[self._sample_rate] << 4)

    # Turning off CLK_CHP
    self._bus.write_byte_data(self._device_address,
                              NAU7802_Scale_Registers['ADC'], 0x30)

    # Enabling 330pF decoupling cap on channel 2
    self._set_bit(NAU7802_PGA_PWR_Bits['PGA_PWR_PGA_CAP_EN'],
                  NAU7802_Scale_Registers['PGA_PWR'], 1)

    # Re-calibrating the analog front-end
    self._set_bit(NAU7802_CTRL2_Bits['CTRL2_CALS'],
                  NAU7802_Scale_Registers['CTRL2'], 1)

    t0 = time()
    while self._cal_afe_status() != NAU7802_Cal_Status['CAL_SUCCESS']:
      if time() - t0 > 1:
        raise TimeoutError("Waited too long for the calibration to occur !")
      if self._cal_afe_status() == NAU7802_Cal_Status['CAL_FAILURE']:
        raise IOError("Calibration failed !")

    if self._backend == 'Pi4' and self._int_pin is not None:
      GPIO.setmode(GPIO.BCM)
      GPIO.setup(self._int_pin, GPIO.IN)

  def get_data(self) -> List[float]:
    """Reads the registers containing the conversion result.

    The output is in Volts by default, and can be converted to Newtons using
    gain and offset.

    Returns:
      :obj:`list`: A list containing the timeframe and the output value
    """

    # Waiting for data to be ready
    t0 = time()
    while not self._data_available():
      if time() - t0 > 0.5:
        raise TimeoutError('Waited too long for data to be ready !')

    out = [time()]

    # Reading the output data
    block = self._bus.read_i2c_block_data(self._device_address,
                                          NAU7802_Scale_Registers['ADCO_B2'],
                                          3)
    value_raw = (block[0] << 16) | (block[1] << 8) | block[2]

    # Converting raw data into Volts or Newtons
    if block[0] >> 7:
      value_raw -= 2 ** 24
    value = value_raw / 2 ** 23 * 0.5 * NAU7802_VREF / self._gain_hardware
    out.append(self._offset + self._gain * value)
    return out

  def close(self) -> None:
    """Powers down the device."""

    # Powering down the device
    self._set_bit(NAU7802_PU_CTRL_Bits['PU_CTRL_PUD'],
                  NAU7802_Scale_Registers['PU_CTRL'], 0)
    sleep(0.001)
    self._set_bit(NAU7802_PU_CTRL_Bits['PU_CTRL_PUA'],
                  NAU7802_Scale_Registers['PU_CTRL'], 0)
    self._bus.close()

    if self._backend == 'Pi4' and self._int_pin is not None:
      GPIO.cleanup()

  def _is_connected(self) -> bool:
    """Tries reading a byte from the device.

    Returns:
      :obj:`bool`: :obj:`True` if reading was successful, else :obj:`False`
    """

    try:
      self._bus.read_byte(self._device_address)
      return True
    except IOError:
      return False

  def _data_available(self) -> bool:
    """Returns :obj:`True` if data is available, :obj:`False` otherwise."""

    # EOC signal from the I2C communication
    if self._int_pin is None:
      return self._get_bit(NAU7802_PU_CTRL_Bits['PU_CTRL_CR'],
                           NAU7802_Scale_Registers['PU_CTRL'])
    # EOC signal from a GPIO
    elif self._backend == 'ft232h':
      return bool(self._bus.get_gpio(self._int_pin))
    else:
      return bool(GPIO.input(self._int_pin))

  def _set_bit(self,
               bit_number: int,
               register_address: int,
               bit: int) -> None:
    """Sets a given bit in the specified register.

    Args:
      bit_number (:obj:`int`): Position of the bit in the register
      register_address (:obj:`int`): Index of the register
      bit (:obj:`int`): Value of the bit
    """

    value = self._bus.read_i2c_block_data(self._device_address,
                                          register_address, 1)[0]
    if bit:
      value |= (1 << bit_number)
    else:
      value &= ~(1 << bit_number)
    self._bus.write_byte_data(self._device_address, register_address, value)

  def _get_bit(self,
               bit_number: int,
               register_address: int) -> bool:
    """Reads a given bit in the specified register.

    Args:
      bit_number (:obj:`int`): Position of the bit in the register
      register_address (:obj:`int`): Index of the register

    Returns:
      :obj:`bool`: True if the bit value is 1, else False
    """

    value = self._bus.read_i2c_block_data(self._device_address,
                                          register_address, 1)[0]
    value = value >> bit_number & 1
    return bool(value)

  def _cal_afe_status(self) -> int:
    """Reads the calibration status bits.

    Returns:
      :obj:`int`: The int value corresponding to the current calibration status
    """

    if self._get_bit(NAU7802_CTRL2_Bits['CTRL2_CAL_ERROR'],
                     NAU7802_Scale_Registers['CTRL2']):
      return NAU7802_Cal_Status['CAL_FAILURE']
    elif self._get_bit(NAU7802_CTRL2_Bits['CTRL2_CALS'],
                       NAU7802_Scale_Registers['CTRL2']):
      return NAU7802_Cal_Status['CAL_IN_PROGRESS']
    else:
      return NAU7802_Cal_Status['CAL_SUCCESS']
