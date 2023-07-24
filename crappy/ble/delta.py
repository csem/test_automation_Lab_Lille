
import crappy
import time
import pyvisa
from .ble import BLE
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



class Delta(BLE,LoggerPerso):

    def __init__(self):
        try:
            class_name=__name__
            LoggerPerso.__init__(self,class_name)
            self.logger.info(" Initialization of the device ...")
 
            self.api=None
            self.bool_res=False
            self.device_name=None
            self.mac_address=None
            self.event = Event()
            self.scan_interval = 15  # or whatever you want your scan interval to be
            self.logger.info(" Initialization done !")
        except Exception as e:
            self.logger.info(" Error : initialization of the device is incorrect ")


       
    def flash_firmware_ota_dfu(self, version_firm, name_device):
        command = f"nrfutil dfu ble -ic NRF52 -pkg sandbox/artifacts/app_{version_firm}.zip -p {self.mac_address} -n {name_device}  -f"
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            self.logger.error('Erreur lors de l\'exécution de la commande : %s', stderr.decode())
            return False
        else:
            self.logger.info('Résultats de la commande : %s', stdout.decode())
            return True

    def get_all_delta(self):
        adapter = self.initialize_adapter()
        device_prefix = "DELTA_00"
        address_l = []
        devices = adapter.scan()
        for device in devices:
            if device['name'].startswith(device_prefix) and device['address'] not in address_l:
                address_l.append(device['address'])
        adapter.stop()

        return address_l


    def get_uuid(self, uuid_type):
        uuid_dict = {
            "firm_version": "00002a26-0000-1000-8000-00805f9b34fb",
            "model_number": "00002a24-0000-1000-8000-00805f9b34fb",
            "serial_number": "00002a25-0000-1000-8000-00805f9b34fb",
            "manufact_name": "00002a29-0000-1000-8000-00805f9b34fb",
            "battery_level": "00002a19-0000-1000-8000-00805f9b34fb"
        }
        return uuid_dict.get(uuid_type)


