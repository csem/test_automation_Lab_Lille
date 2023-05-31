import crappy
import time
import pyvisa
import logging
from datetime import datetime

class General():

    def __init__(self,id_device):
        
        self.id_device=id_device
        self.ressource=pyvisa.ResourceManager()
        self.instr=None

    def __open__(self):
        self.logger.info("Opening of device ...")
        try:
            self.instr=self.ressource.open_resource(self.id_device)
        
            self.instr.baud_rate = 1000000
            self.instr.write('*CLS')
            self.instr.write('*RST')
            self.logger.info("Opening done !")
        except Exception as e:
            self.logger.error("Error: device is not opened. Check if your id is good or if the device is connected.")
       
 

    def __get_idn__(self):

        self.logger.info("Getting IDN ...")
        try:
            var_temp=self.instr.query('*IDN?')
            self.logger.info("IDN is : "+str(var_temp))
            self.logger.info("IDN done !")
        except Exception as e:
            self.logger.error(" Error : IDN has not be obtained")



 
        return var_temp
    
    def __close__(self):
        self.ressource.close()
        self.instr.close()

