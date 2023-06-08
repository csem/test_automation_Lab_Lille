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
class Delta(InOut,LoggerPerso):

    def __init__(self):
        try:
            class_name=__name__
            LoggerPerso.__init__(self,class_name)
            self.logger.info(" Initialization of the device ...")
            super().__init__()
            self.api=None
            self.bool_res=False

            self.logger.info(" Initialization done !")
        except Exception as e:
            self.logger.info(" Error : initialization of the device is incorrect ")


    def open(self):
        pass
     
    def connexion_bluetooth(self,id):
        self.logger.info("Begin testing bluetooth connexion ...")
     
        async def run():
            scanner = BleakScanner()
            devices = await scanner.discover()

            for device in devices:
                pass

            async with BleakClient(id) as client:
                print(f"Connected: {client.is_connected}")

                self.bool_res=client.is_connected

        loop = asyncio.get_event_loop()
        loop.run_until_complete(run())
        res=self.bool_res
        self.bool_res=False
        self.logger.info(self.bool_res)
        self.logger.info("Bluetooth connexion is ok !")
        return res

    def read_bluetooth(self,id,data_adress):
        async def run():
                scanner = BleakScanner()
                devices = await scanner.discover()

                
                async with BleakClient(id) as client:
                

                    try:
                        value = await client.read_gatt_char(data_adress)
                        self.bool_res=True
                    except Exception as e:
                        print(e)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(run())
        res=self.bool_res
        self.bool_res=False
        self.logger.info(self.bool_res)
        return res

            
    

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

        command = f"nrfutil nrf5sdk-tools dfu ble -ic NRF52 -pkg artifacts/app_{version_firm}.zip -p {id_device}-n "{name_device}"  -f" 
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            print(f'Erreur lors de l\'exécution de la commande : {stderr.decode()}')
            return False
        else:
            print(f'Résultats de la commande : {stdout.decode()}')
                return True


    def get_data(self):
        return [time.time(), 0]

    def set_cmd(self, cmd):
        pass

    def close(self):
        pass
