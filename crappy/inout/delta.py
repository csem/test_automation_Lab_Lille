import crappy
import time
import pyvisa
from .inout import InOut
from datetime import datetime
from .general_class import General
from .general_class import LoggerPerso
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
class Delta(InOut,LoggerPerso):

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

    def flash_firmware_jlink(self):
        with LowLevel.API('NRF52') as api:
            self.logger.info("Opening connection with JLINK ...")
            self.connect_to_api(api, 821005840, "Connection done !")
            self.logger.info("Opening connection with device ...")
            self.connect_to_api(api, None, "Connection done !")

            try:
                self.logger.info("Beginning reset and flashing...")
                api.sys_reset()
                api.erase_all()
                self.logger.info("Reset done !")
                api.program_file("sandbox/full.hex")
                self.logger.info("Flashing done!")
                api.sys_reset()
                api.go()
                self.logger.info("Reset after flash done!")
                api.close()
                self.logger.info("Everything done! Device is ready to be used")
                return True
            except Exception as e:
                self.logger.error("Error during flashing: %s", e)
                return False

    def flash_firmware_ota_dfu(self, id_device, version_firm, name_device):
        command = f"nrfutil dfu ble -ic NRF52 -pkg sandbox/artifacts/app_{version_firm}.zip -p {id_device} -n {name_device}  -f"
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
            result_addresses = []
            adapter = self.initialize_adapter()
            devices = adapter.scan()
            for device in devices:
                if device['name'] == device_name:
                    self.mac_address = device['address']
                    result_addresses.append(self.mac_address)
                    adapter.stop()
            print(f" res adress : {result_addresses}")
            if result_addresses:  # Check if the list is not empty
                return result_addresses[0]
            else:
                return None 

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

    def get_uuid(self, uuid_type):
        uuid_dict = {
            "firm_version": "00002a26-0000-1000-8000-00805f9b34fb",
            "model_number": "00002a24-0000-1000-8000-00805f9b34fb",
            "serial_number": "00002a25-0000-1000-8000-00805f9b34fb",
            "manufact_name": "00002a29-0000-1000-8000-00805f9b34fb",
            "battery_level": "00002a19-0000-1000-8000-00805f9b34fb"
        }
        return uuid_dict.get(uuid_type)


    def get_device_info(self, device_name,info_type,uuid=None):
        if uuid==None:
            uuid=self.get_uuid(info_type)
        address = self.get_add_mac(device_name)
        print(f"uuid : {uuid}")
        print(f"adress : {address}")
        info_value = self.get_value_from_device(uuid, address)
        self.logger.info(f"{info_type}: {info_value.decode()}")
        return info_value
    
    def get_device_infos(self, device_name,info_type,uuid=None):
        if uuid==None or len(info_type)!=len(uuid):
            uuid=[]
            for x in info_type:
                uuid.append([x,self.get_uuid(info_type)])
        address = self.get_add_mac(device_name)
        info_value = self.get_values_from_device(uuid, address)
        self.logger.info(f"{info_type}: {info_value}")
        return info_value
    




    def get_data(self):
        return [time.time(), 0]

    def set_cmd(self, cmd):
        pass

    def close(self):
        pass
