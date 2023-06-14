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
        async def is_device_available(device_address):
            client = BleakClient(device_address)
            try:
                return await client.connect()
            finally:
                if client.is_connected:
                    await client.disconnect()  

        command = f"nrfutil nrf5sdk-tools dfu ble -ic NRF52 -pkg sandbox/artifacts/app_{version_firm}.zip -p {id_device} -n {name_device}  -f" 
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            print(f'Erreur lors de l\'exécution de la commande : {stderr.decode()}')
            return False
        else:
            print(f'Résultats de la commande : {stdout.decode()}')
            process.wait()


            loop = asyncio.get_event_loop()
            device_is_available = loop.run_until_complete(is_device_available(id_device))
            if not device_is_available:
                print('L\'appareil n\'est pas disponible après le flashage.')
                return False
            return True
    def get_all_delta(self):
        def handle_discovery(device, advertisement_data):
            device_prefix = "DELTA_00"
            if advertisement_data[0].startswith(device_prefix) and device.address not in address_l:
                address_l.append(device.address)

        async def run():
            scanner = BleakScanner()
            scanner.register_detection_callback(handle_discovery)
      
            await scanner.start()
            await asyncio.sleep(15)
            await scanner.stop()


        address_l = []
        loop = asyncio.get_event_loop()
        loop.run_until_complete(run())
        return address_l


    def get_add_mac(self,device_name):
        async def get_addd_mac(device_name):
            scanner = BleakScanner()
            devices = await scanner.discover()

            for device in devices:
                if device.name == device_name:
                    return device.address

            return None

        loop = asyncio.new_event_loop()
        # Le définir comme boucle d'événements par défaut
        asyncio.set_event_loop(loop)
        try:
            # Exécuter la fonction get_add_mac
            address = loop.run_until_complete(get_add_mac(device_name))
        finally:
            # Fermer la boucle d'événements
            loop.close()


        if address:
            print(f"Adresse MAC de {device_name}: {address}")
        else:
            print(f"Appareil {device_name} non trouvé")

        return address

    def get_value_from_device(self,uuid,address):
        res_value=[]
        async def run(address):
            async with BleakClient(address) as client:
                print(f"Connected: {client.is_connected}")

                value = await client.read_gatt_char(uuid)
                res_value.append(value)
                print(f"Value: {value}")


        loop = asyncio.get_event_loop()
        loop.run_until_complete(run(address))
        return res_value[0]
    
    def get_multiple_value_from_device(self,uuid,address,time):
        def callback(sender: int, data: bytearray):
            res_l.append(data)
        async def run(address,uuid,time):

            async with BleakClient(address) as client:
                print(f"Connected: {client.is_connected}")
        
                await client.start_notify(uuid, callback)
                await asyncio.sleep(time)  
                await client.stop_notify(uuid)

        res_l = []
        loop = asyncio.get_event_loop()
        loop.run_until_complete(run(address,uuid,time))
        return res_l
    

    def __sub_decode_bytearray_int(self,mapping):
        return int(''.join(str(mapping[b]) for b in data3))

    def decode_bytearray(self,bytearray,device_name,get_function_name):
        firm=self.get_firm_version(device_name)
        v_firm=firm.split("+")

        if v_firm=="v1.1.114":
            if get_function_name=="get_height":
                mapping = {1: 2, 33: 10, 159: 2, 237: 10}
                return self.__sub_decode_bytearray_int(mapping)
            elif get_function_name=="get_weight":
                mapping = {109: 2, 28: 10}
                return self.__sub_decode_bytearray_int(mapping)



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
    

    ###################### GET BATTERY INFORMATIONS ###########################

    def get_battery_level(self,device_name,uuid="00002a19-0000-1000-8000-00805f9b34fb"):
        address=self.get_add_mac(device_name)
        battery_level=self.get_value_from_device(uuid,address)
        return battery_level[0]
    
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
