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
        self.instr=self.ressource.open_resource(self.id_device)
        
        self.instr.baud_rate = 1000000
        self.instr.write('*CLS')
        self.instr.write('*RST')
 

    def __get_idn__(self):
      
        var_temp=self.instr.query('*IDN?')
 
        return var_temp
    
    def __close__(self):
        self.ressource.close()
        self.instr.close()

