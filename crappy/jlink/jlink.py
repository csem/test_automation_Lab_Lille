
from time import time, sleep
from typing import Optional, Dict, Any, Union, List
import numpy as np

from .._global import DefinitionError
from pynrfjprog import API, HighLevel,LowLevel

import pylink
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
        self.api = pylink.JLink()
        self.connected = False
        self.rtt = None

    def open(self, id):
        try:
            self.api.open()
            self.api.connect(id)
            self.connected = True
        except LowLevel.APIError as e:
            self.connected = False
            raise Exception(f"Error: Impossible to connect to the NRF device. {e}")

    def close(self):
        if self.rtt is not None:
            self.api.rtt_stop()
        self.api.close()
        self.connected = False


    def set_cmd(self, *cmd):
        if self.connected:
            pass
        else:
            raise RuntimeError("NRF device is not connected.")

   