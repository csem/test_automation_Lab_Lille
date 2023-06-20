
from time import time, sleep
from typing import Optional, Dict, Any, Union, List
import numpy as np

from .._global import DefinitionError
from pynrfjprog import API, HighLevel,LowLevel

class MetaJLINK(type):
  """Metaclass ensuring that two JLINK don't have the same name, and that all
  JLINK define the required methods. Also keeps track of all the JLINK
  classes, including the custom user-defined ones."""

  classes = {}

  def __new__(mcs, name: str, bases: tuple, dct: dict) -> type:
    return super().__new__(mcs, name, bases, dct)

  def __init__(cls, name: str, bases: tuple, dct: dict) -> None:
    super().__init__(name, bases, dct)

    # Checking that an JLINK with the same name doesn't already exist
    if name in cls.classes:
      raise DefinitionError(f"The {name} class is already defined !")

    # Saving the class
    if name != 'JLINK':
      cls.classes[name] = cls




class JLINK(metaclass=MetaJLINK):   
    def __init__(self):
        self.api = LowLevel.API()
        self.connected = False
        self.rtt = None

    def open(self, device_family):
        try:
            self.api.open()
            self.api.connect_to_emu_with_snr(device_family)
            self.connected = True
        except LowLevel.APIError as e:
            self.connected = False
            raise Exception(f"Error: Impossible to connect to the NRF device. {e}")

    def close(self):
        if self.rtt is not None:
            self.api.rtt_stop()
        self.api.disconnect_from_emu()
        self.api.close()
        self.connected = False

    def get_data(self):
        if self.connected:
            data = None
            # Code to get the data from the NRF device
            return data
        else:
            raise RuntimeError("NRF device is not connected.")

    def set_cmd(self, *cmd):
        if self.connected:
            # Code to handle commands
            pass
        else:
            raise RuntimeError("NRF device is not connected.")

    def start_rtt(self):
        if self.connected:
            self.api.rtt_start()
            self.rtt = True
        else:
            raise RuntimeError("NRF device is not connected.")

    def stop_rtt(self):
        if self.connected and self.rtt:
            self.api.rtt_stop()
            self.rtt = False
        else:
            raise RuntimeError("NRF device is not connected.")

    def read_rtt(self, up_channel_index=0, length=1024):
        if self.connected and self.rtt:
            return self.api.rtt_read(up_channel_index, length)
        else:
            raise RuntimeError("NRF device is not connected.")

    def write_rtt(self, down_channel_index=0, data=None):
        if self.connected and self.rtt and data is not None:
            return self.api.rtt_write(down_channel_index, data)
        else:
            raise RuntimeError("NRF device is not connected.")

    def start_stream(self):
        if self.connected:
            # Code to start stream acquisition
            pass
        else:
            raise RuntimeError("NRF device is not connected.")

    def get_stream(self):
        if self.connected:
            stream_data=None
            # Code to get stream data from the NRF device
            return stream_data
        else:
            raise RuntimeError("NRF device is not connected.")

    def stop_stream(self):
        if self.connected:
            # Code to stop stream acquisition
            pass
        else:
            raise RuntimeError("NRF device is not connected.")
        
    
    def read_data(self, addr, data_len):
        if self.connected:
            return self.api.read(addr, data_len)
        else:
            raise RuntimeError("NRF device is not connected.")
    
    def flash_firmware(self, firmware_path):
        if self.connected:
            try:
                self.logger.info("Beginning reset and flashing...")
                self.api.sys_reset()
                self.api.erase_all()
                self.logger.info("Reset done !")
                self.api.program_file(firmware_path)
                self.logger.info("Flashing done!")
                self.api.sys_reset()
                self.api.go()
                self.logger.info("Reset after flash done!")
                return True
            except Exception as e:
                self.logger.error("Error during flashing: %s", e)
                return False
        else:
            raise RuntimeError("NRF device is not connected.")