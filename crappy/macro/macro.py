
from time import time, sleep
from typing import Optional, Dict, Any, Union, List
import numpy as np
from docx import Document
from pyppeteer import launch
import pyautogui
from .._global import DefinitionError

class MetaMACRO(type):
  """Metaclass ensuring that two MACRO don't have the same name, and that all
  macro define the required methods. Also keeps track of all the macro
  classes, including the custom user-defined ones."""

  classes = {}

  def __new__(mcs, name: str, bases: tuple, dct: dict) -> type:
    return super().__new__(mcs, name, bases, dct)

  def __init__(cls, name: str, bases: tuple, dct: dict) -> None:
    super().__init__(name, bases, dct)

    # Checking that an macro with the same name doesn't already exist
    if name in cls.classes:
      raise DefinitionError(f"The {name} class is already defined !")

    # Saving the class
    if name != 'MACRO':
      cls.classes[name] = cls




class MACRO(metaclass=MetaMACRO):
    def __init__(self):
        self.gui=pyautogui
        self.browser=None
        self.page=None
        self.playwright=None

    def open(self, id):
        pass

    def close(self):
        pass


    def set_cmd(self, *cmd):
        pass
    
    def press_keys(self,keys):
      self.gui.press(keys)

    def write_keys(self,keys):
      self.gui.write(keys)

    def press_hotkeys(self,hotkeys):
      self.gui.hotkey(hotkeys)
          

   