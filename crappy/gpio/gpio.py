
from time import time, sleep
from typing import Optional, Dict, Any, Union, List
import numpy as np

from .._global import DefinitionError

class MetaGPIO(type):
  """Metaclass ensuring that two GPIO don't have the same name, and that all
  GPIO define the required methods. Also keeps track of all the GPIO
  classes, including the custom user-defined ones."""

  classes = {}

  def __new__(mcs, name: str, bases: tuple, dct: dict) -> type:
    return super().__new__(mcs, name, bases, dct)

  def __init__(cls, name: str, bases: tuple, dct: dict) -> None:
    super().__init__(name, bases, dct)

    # Checking that an GPIO with the same name doesn't already exist
    if name in cls.classes:
      raise DefinitionError(f"The {name} class is already defined !")

    # Saving the class
    if name != 'GPIO':
      cls.classes[name] = cls




class GPIO(metaclass=MetaGPIO):   
    def __init__(self):
        pass

    def open(self, id):
        pass

    def close(self):
        pass