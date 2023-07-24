
from time import time, sleep
from typing import Optional, Dict, Any, Union, List
import numpy as np

from .._global import DefinitionError

import crappy
import time
import pyvisa
from datetime import datetime
from ..general_class import LoggerPerso

from ..general_class import General
import logging
from pynrfjprog import LowLevel
import asyncio
from bleak import BleakClient, BleakScanner
import subprocess
import inspect
from pygatt.backends import GATTToolBackend
from pygatt.exceptions import (
    BLEError, NotConnectedError, NotificationTimeout
)
import pygatt
from threading import Event
import time
import struct
class MetaBLE(type):
  """Metaclass ensuring that two BLE don't have the same name, and that all
  BLE define the required methods. Also keeps track of all the BLE
  classes, including the custom user-defined ones."""

  classes = {}

  def __new__(mcs, name: str, bases: tuple, dct: dict) -> type:
    return super().__new__(mcs, name, bases, dct)

  def __init__(cls, name: str, bases: tuple, dct: dict) -> None:
    super().__init__(name, bases, dct)

    # Checking that an BLE with the same name doesn't already exist
    if name in cls.classes:
      raise DefinitionError(f"The {name} class is already defined !")

    # Saving the class
    if name != 'BLE':
      cls.classes[name] = cls




class BLE(LoggerPerso,metaclass=MetaJBLE):   
    def __init__(self):
        try:
            class_name=__name__
            LoggerPerso.__init__(self,class_name)
            self.logger.info(" Initialization of the device ...")
            super().__init__()
            self.api=None
            self.bool_res=False
            self.device_name=None
            self.mac_address=None
            
            self.event = Event()
            self.scan_interval = 15  # or whatever you want your scan interval to be

            self.logger.info(" Initialization done !")
        except Exception as e:
            self.logger.info(" Error : initialization of the device is incorrect ")


    def open(self):
        pass
     

    def connect_to_api(self, api, target, msg):
        try:
            api.open()
            api.connect_to_emu_with_snr(target)
            self.logger.info(msg)
        except Exception as e:
            self.logger.error("Error during connection: %s", e)





    @staticmethod
    def initialize_adapter():
        adapter = pygatt.BGAPIBackend()
        adapter.start()
        time.sleep(1)
        return adapter

    def get_add_mac(self, device_name):
        if self.mac_address is not None:
            return self.mac_address
        else:
            res_l = []
            adapter = self.initialize_adapter()
            devices = adapter.scan()
            for device in devices:
                if device['name'] == device_name:
                    self.mac_address = device['address']
                    res_l.append(self.mac_address)
                    adapter.stop()
            return res_l[0]

    def get_value_from_device(self, uuid, address):
        adapter = self.initialize_adapter()
        time.sleep(10)
        try:
            device = adapter.connect(address, address_type=pygatt.BLEAddressType.random)
            self.event.wait(10)

            value = device.char_read(uuid)
            adapter.stop()

            self.event.wait(self.scan_interval)
            return value

        except (BLEError, NotConnectedError, NotificationTimeout) as ex:
            self.logger.error("Exception: %s", ex)

    def get_values_from_device(self, uuid, address):
        adapter = self.initialize_adapter()
        time.sleep(10)
        try:
            device = adapter.connect(address, address_type=pygatt.BLEAddressType.random)
            self.scan_event.wait(10)
            values = []
            for id in uuid:
                values.append([id[0], device.char_read(id[1])])
            adapter.stop()

            self.scan_event.wait(self.scan_interval)
            return values

        except (BLEError, NotConnectedError, NotificationTimeout) as ex:
            self.logger.error("Exception: %s", ex)

    


    def get_device_info(self, device_name,info_type,uuid):
        address = self.get_add_mac(device_name)
        info_value = self.get_value_from_device(uuid, address)
        self.logger.info(f"{info_type}: {info_value.decode()}")
        return info_value
    
    def get_device_infos(self, device_name,uuid):
        """
        UUID need to be like this = [["Name_uuid",value_uuid],[]...]

        """
        address = self.get_add_mac(device_name)
        info_value = self.get_values_from_device(uuid, address)
        self.logger.info(f"{info_type}: {info_value}")
        return info_value
    
