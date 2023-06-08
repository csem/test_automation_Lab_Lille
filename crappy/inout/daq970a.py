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

    
    def get_one_measure(self, measurement_type:str,volt_type=None,amp_type=None,range_measure="DEFAULT",resolution_measure="DEFAULT")->list[float]:
        self.logger.info("Getting Measure at t time of channel  ")
        tab_res = []
        try:
            for channel in self.channels.split(":"):
                self.logger.info(f"Getting the measure for channel {channel}")
                if measurement_type.lower() == "volt":
                    measure = float(self.instr.query(f":MEASure:VOLTage:{volt_type}? {range_measure},{resolution_measure},(@{channel})"))
                elif measurement_type.lower() == "ampere":
                    measure = float(self.instr.query(f":MEASure:CURRent:{amp_type}? {range_measure},{resolution_measure},(@{channel})"))
                elif measurement_type.lower() == "resistance":
                    measure = float(self.instr.query(f":MEASure:FRESistance? {range_measure},{resolution_measure},(@{channel})"))
                else:
                    self.logger.error("Invalid measurement type. Valid types are: 'volt', 'ampere', 'resistance'.")
                    return False
                tab_res.append(measure)
                self.logger.info("Measure done : "+str(measure))
            self.logger.info("All measure are done ")

        except Exception as e:
            self.logger.error("Error : The measure was not done correctly. Check if the channel are correct or if the config is correct")
        return tab_res


    
    def get_measure_over_time(self,  measurement_type,volt_type=None,amp_type=None,range_measure="DEFAULT",resolution_measure="DEFAULT",trigger_delay=0.2,count=100,timeout=1000)-> list[float]:
        # More Generalisation !
        self.logger.info("Test getting measure for X time negim ... ")
        nbr_of_channel=len(self.channels.split(":"))

        self.logger.info("Begin configuratation ...")
        try:
            if measurement_type.lower() == "volt":
                self.instr.write(f":CONFigure:VOLTage:{volt_type} {range_measure},{resolution_measure},(@{self.channels})")
            elif measurement_type.lower() == "ampere":
                self.instr.write(f":CONFigure:CURRent:{amp_type} {range_measure},{resolution_measure},(@{self.channels})")
            elif measurement_type.lower() == "resistance":
                self.instr.write(f":CONFigure:FRESistance {range_measure},{resolution_measure},(@{self.channels})")
            else:
                self.logger.error("Invalid measurement type. Valid types are: 'volt', 'ampere', 'resistance'.")
                return False
            

            self.instr.write(':TRIGger:COUNt %G' % (count))
            self.instr.write(':TRIGger:SOURce %s' % ('TIMer'))
            self.instr.write(':TRIGger:TIMer %G' % (trigger_delay))
            self.instr.write(':INITiate')

            start_time = datetime.now()
            self.logger.info("Configuration done !")

            time.sleep(0.2)
                    
            self.logger.info("Measure begin ...")

            self.instr.write(':FETCh?')
            self.instr.timeout = (count*trigger_delay)*timeout 
            try:
                data_list  = self.instr.read().rstrip('\n').split(',')
            except:
                print('Error: Time step too short')
                return [[0] for i in range(nbr_of_channel)], 0, 0
            end_time = datetime.now()
            self.instr.timeout = 2000 
            value_list = [float(x) for x in data_list]
            self.logger.info("Mesure done !")
            return [value_list[i::nbr_of_channel] for i in range(nbr_of_channel)], start_time, end_time

        except Exception as e:
            self.logger.error(f"Error : {e}")
            return False




    def get_data(self):
        return [time.time(), 0]

    def set_cmd(self, cmd):
        pass

    def close(self):
        pass
