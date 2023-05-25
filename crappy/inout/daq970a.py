import crappy
import time
import pyvisa
from .inout import InOut
from datetime import datetime
from .general_class import General
import logging
class Daq970a(InOut,General):

    def __init__(self,id_device,channels):

        super().__init__()
        General.__init__(self,id_device)
        self.channels=channels
        self.ressource=pyvisa.ResourceManager()
        self.instr=None




    def open(self):
        """_summary_
        """
        pass
     
    def get_channels(self):
        return self.channels.split(":")
    

    def beeper(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        bool_res=False
        try:
            self.instr.write(':SYSTem:BEEPer')
        except Exception as e:
            bool_res=True
        return bool_res

    
       
    def get_measure(self):
        self.logger.info("Getting Measure at t time of channel  ")
        tab_res=[]
        for channel in self.channels.split(":"):
            self.logger.info("Getting the measure for channel "+str(channel))
            measure=float(self.instr.query(":MEASure:FRESistance? 10000,DEFault,(@"+channel+")"))
            tab_res.append(measure)
            self.logger.info("Measure done : "+str(measure))
        self.logger.info("All measure are done ")
        return tab_res

    
    def complex_test(self):
            nbr_of_channel=len(self.channels.split(":"))
            count=100
            trigger_delay=0.20
        
            self.instr.write(":CONFigure:FRESistance 10000,DEFault,(@"+self.channels+")")
            self.instr.write(':TRIGger:COUNt %G' % (count))
            self.instr.write(':TRIGger:SOURce %s' % ('TIMer'))
            self.instr.write(':TRIGger:TIMer %G' % (trigger_delay))
            self.instr.write(':INITiate')
    
            start_time = datetime.now()
            
            time.sleep(0.2)
            self.instr.write(':FETCh?')
            self.instr.timeout = (count*trigger_delay)*1000 #set timeout
            try:
                data_list  = self.instr.read().rstrip('\n').split(',')
            except:
                print('Error: Time step too short')
                return [[0] for i in range(nbr_of_channel)], 0, 0
            end_time = datetime.now()
            self.instr.timeout = 2000 #restore standard value
            value_list = [float(x) for x in data_list]
            return [value_list[i::nbr_of_channel] for i in range(nbr_of_channel)], start_time, end_time
                


    def get_data(self):
        return [time.time(), 0]

    def set_cmd(self, cmd):
        pass

    def close(self):
        pass
