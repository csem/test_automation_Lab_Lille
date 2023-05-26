import crappy
import time
import pyvisa
import logging
from datetime import datetime
logging.basicConfig(filename='my_logfile.log', level=logging.DEBUG,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class General():

    def __init__(self,id_device):
        
        self.id_device=id_device
        self.ressource=pyvisa.ResourceManager()
        self.instr=None
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler('mon_application.log')
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.info(" TEST begin ...")
    

        

    def __open__(self):
        self.logger.info("Opening of device ...")
        self.instr=self.ressource.open_resource(self.id_device)
        
        self.instr.baud_rate = 1000000
        self.instr.write('*CLS')
        self.instr.write('*RST')
        self.logger.info("Opening done !")

    def __get_idn__(self):
        self.logger.info("Getting IDN ...")
        var_temp=self.instr.query('*IDN?')
        self.logger.info("IDN is ok !")
        return var_temp
    
    def __close__(self):
        self.ressource.close()
        self.instr.close()

    def __get_logger__(self):
        return self.logger
