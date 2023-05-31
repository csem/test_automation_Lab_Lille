import crappy
import time
import pyvisa
from .inout import InOut
from datetime import datetime
from .general_class import General
from .general_class import LoggerPerso
import logging
class Daq970a(InOut,General,LoggerPerso):

    def __init__(self,id_device,channels):
        try:
            class_name=__name__
            LoggerPerso.__init__(self,class_name)
            self.logger.info(" Initialization of the device ...")
            super().__init__()
            General.__init__(self,id_device)
            self.channels=channels
            self.ressource=pyvisa.ResourceManager()
            self.instr=None

            self.logger.info(" Initialization done !")
        except Exception as e:
            self.logger.info(" Error : initialization of the device is incorrect ")


    def open(self):

        pass
     
    def get_channels(self):
        return self.channels.split(":")
    

    def beeper(self):
        self.logger.info("Testing beeper ...")
        bool_res=False
        try:
            self.instr.write(':SYSTem:BEEPer')
            self.logger.info("Beeper is ok !")
        except Exception as e:
            self.logger.error("Error : Beeper was not done correctly")
            bool_res=True
        return bool_res

    
       
    def get_measure(self):
        self.logger.info("Getting Measure at t time of channel  ")
        tab_res=[]
        try:
            for channel in self.channels.split(":"):
                self.logger.info("Getting the measure for channel "+str(channel))
                measure=float(self.instr.query(":MEASure:FRESistance? 10000,DEFault,(@"+channel+")"))
                tab_res.append(measure)
                self.logger.info("Measure done : "+str(measure))
            self.logger.info("All measure are done ")

        except Exception as e:
            self.logger.error("Error : The measure was not done correctly. Check if the channel are correct or if the config is correct")
        return tab_res

    
    def complex_test(self):
            self.logger.info("Complex Test begin ... ")
            nbr_of_channel=len(self.channels.split(":"))
            count=100
            trigger_delay=0.20
            self.logger.info("Begin configuratation ...")
            try:
                self.instr.write(":CONFigure:FRESistance 10000,DEFault,(@"+self.channels+")")
                self.instr.write(':TRIGger:COUNt %G' % (count))
                self.instr.write(':TRIGger:SOURce %s' % ('TIMer'))
                self.instr.write(':TRIGger:TIMer %G' % (trigger_delay))
                self.instr.write(':INITiate')
        
                start_time = datetime.now()
                self.logger.info("Configuration done !")

                time.sleep(0.2)
                        
                self.logger.info("Measure begin ...")

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
                self.logger.info("Mesure done !")
            except Exception as e:
                self.logger.error("Error")

            return [value_list[i::nbr_of_channel] for i in range(nbr_of_channel)], start_time, end_time
                


    def get_data(self):
        return [time.time(), 0]

    def set_cmd(self, cmd):
        pass

    def close(self):
        pass
