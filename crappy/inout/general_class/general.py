import crappy
import time
import pyvisa

from datetime import datetime

class General():

    def __init__(self,id_device):
        
        self.id_device=id_device
        self.ressource=pyvisa.ResourceManager()
        self.instr=None
        

    def __open__(self):
        self.instr=self.ressource.open_resource(self.id_device)
        
        self.instr.baud_rate = 1000000
        self.instr.write('*CLS')
        self.instr.write('*RST')

    def __get_idn__(self):
        return self.instr.query('*IDN?')
    
    def __close__(self):
        self.ressource.close()
        self.instr.close()

