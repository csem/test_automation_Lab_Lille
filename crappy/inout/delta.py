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
     

    

    def flash_firmware_jlink(self):
        bool_res=False
        with LowLevel.API('NRF52') as api:
            self.logger.info("Open connection with JLINK ...")
            try:
                api.open()
                api.connect_to_emu_with_snr(821005840)
                self.logger.info("Connection done !")
            except Exception as e:
                pass
            
            self.logger.info("Open connection with device ...")
            try:
                api.connect_to_device()
                self.logger.info("Connection done !")
            except Exception as e:
                pass

    
            try:
                self.logger.info("Begin reset and flashing...")

                api.sys_reset()
                api.erase_all()
                self.logger.info("Reset done !")

                api.program_file("sandbox/full.hex")

                        
                self.logger.info("Flashing done!")

                api.sys_reset()
                api.go()
                self.logger.info("reset after flash done !")

                api.close()
                self.logger.info("Everything done! Device is ready to be used")

                bool_res=True
            except Exception as e:
                pass
        return bool_res
            
    def flash_firmware_ota_dfu(self,id_device,version_firm,name_device):

        command = f"nrfutil nrf5sdk-tools dfu ble -ic NRF52 -pkg sandbox/artifacts/app_{version_firm}.zip -p {id_device} -n {name_device}  -f" 
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            print(f'Erreur lors de l\'exécution de la commande : {stderr.decode()}')
            return False
        else:
            print(f'Résultats de la commande : {stdout.decode()}')
            return True
        
    def get_all_delta(self):
        self.adapter.start()
        self.adapter 
        device_prefix = "DELTA_00"
        address_l = []
        devices = self.adapter.scan()
        for device in devices:
            if device['name'].startswith(device_prefix) and device['address'] not in address_l:
                address_l.append(device['address'])
        self.adapter.stop()

        return address_l

    def get_add_mac(self,device_name):

        if self.mac_address is not None:

            return self.mac_address
        else:
            res_l=[]
            adapter=pygatt.GATTToolBackend()
            adapter.start()
            time.sleep(1)
            devices = adapter.scan()
            for device in devices:
                if device['name'] == device_name:

                    self.mac_address = device['address']
                    res_l.append(self.mac_address)
                    adapter.stop()
      
                
            adapter.reset()
            return res_l[0]




    def get_value_from_device(self,uuid,address):
        adapter=pygatt.GATTToolBackend()
        adapter.start()
        time.sleep(1)
        try:
            device = adapter.connect(address,address_type=pygatt.BLEAddressType.random)
            self.event.wait(1)

            value = device.char_read(uuid)
            return value

        except (BLEError, NotConnectedError, NotificationTimeout) as ex:
            print(f"Exception: {str(ex)}")
        finally:
            adapter.stop()
            adapter.reset()

            self.event.wait(self.scan_interval)

    ###################### GET GENERAL INFORMATIONS ###########################

    def get_firm_version(self,device_name,uuid="00002a26-0000-1000-8000-00805f9b34fb"):
        address=self.get_add_mac(device_name)
        version_firm=self.get_value_from_device(uuid,address)
        return version_firm.decode()

    def get_model_number(self,device_name,uuid="00002a24-0000-1000-8000-00805f9b34fb"):
        address=self.get_add_mac(device_name)
        model_number=self.get_value_from_device(uuid,address)
        return model_number.decode()

    def get_serial_number(self,device_name,uuid="00002a25-0000-1000-8000-00805f9b34fb"):
        address=self.get_add_mac(device_name)
        serial_number=self.get_value_from_device(uuid,address)
        return serial_number.decode()

    def get_manufact_name(self,device_name,uuid="00002a29-0000-1000-8000-00805f9b34fb"):
        address=self.get_add_mac(device_name)
        manufact_name=self.get_value_from_device(uuid,address)
        return manufact_name.decode()

    def get_battery_level(self,device_name,uuid="00002a19-0000-1000-8000-00805f9b34fb"):
        address=self.get_add_mac(device_name)
        battery_level=self.get_value_from_device(uuid,address)
        return battery_level[0]
    
    ################## NOT UPDATED ################################################
    def get_battery_level_multiple(self,device_name,uuid="00002a19-0000-1000-8000-00805f9b34fb",time=120):
        address=self.get_add_mac(device_name)
        battery_level=self.get_multiple_value_from_device(uuid,address,time)
        return battery_level

    ###################### GET USERS INFORMATIONS ###########################
    def get_age(self, device_name, uuid="00002a80-0000-1000-8000-00805f9b34fb"):
        address = self.get_add_mac(device_name)
        age = self.get_value_from_device(uuid, address)
        return age

    def get_height(self, device_name, uuid="00002a8e-0000-1000-8000-00805f9b34fb"):
        address = self.get_add_mac(device_name)
        height = self.get_value_from_device(uuid, address)
        return height

    def get_weight(self, device_name, uuid="00002a98-0000-1000-8000-00805f9b34fb"):
        address = self.get_add_mac(device_name)
        weight = self.get_value_from_device(uuid, address)
        return weight

    def get_gender(self, device_name, uuid="00002a8c-0000-1000-8000-00805f9b34fb"):
        address = self.get_add_mac(device_name)
        gender = self.get_value_from_device(uuid, address)
        return gender
    
    ###################### GET HEARTH INFORMATIONS ###########################
    def get_body_sensor_location(self, device_name, uuid="00002a38-0000-1000-8000-00805f9b34fb"):
        address = self.get_add_mac(device_name)
        body_sensor_location = self.get_value_from_device(uuid, address)
        return body_sensor_location.decode()

    def get_heart_rate_measurement(self, device_name, uuid="00002a37-0000-1000-8000-00805f9b34fb"):
        address = self.get_add_mac(device_name)
        heart_rate_measurement = self.get_value_from_device(uuid, address)
        return heart_rate_measurement.decode()





    def get_data(self):
        return [time.time(), 0]

    def set_cmd(self, cmd):
        pass

    def close(self):
        pass
