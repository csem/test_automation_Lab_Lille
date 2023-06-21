

from .jlink import JLINK
from pynrfjprog import API, HighLevel,LowLevel
import pylink
import time
import numpy as np

class Global_JLINK(JLINK):


    def ascii_to_int(self,array):
        string = ''.join(chr(digit) for digit in array)
        numbers_str = string.split("\n")

        numbers_str.pop(0)
        numbers_str = numbers_str[:-1]
        numbers = [int(num_str) for num_str in numbers_str if num_str.isdigit()]

        return numbers
    def start_rtt(self):
        if self.connected:
            self.api.rtt_start()
            time.sleep(1)
            self.rtt = True
        else:
            raise RuntimeError("NRF device is not connected.")

    def stop_rtt(self):
        if self.connected and self.rtt:
            self.api.rtt_stop()
            self.rtt = False
        else:
            raise RuntimeError("NRF device is not connected.")

    def read_rtt(self, up_channel_index=0, length=1024):
        if self.connected and self.rtt:

            results = []

            count = 0
            while count < 3:
                num_up = self.api.rtt_get_num_up_buffers()
                for i in range(num_up):
                    time.sleep(1)
                    data = self.api.rtt_read(i, 1024)
                    if data != []:
                        print(f"Len data : {len(data)}")
                        converted_data = self.ascii_to_int(data)
                        print(f"Len conv data : {len(converted_data)}")
                        results.append(converted_data)
                        count += 1
                        break
            return results
        else:
            raise RuntimeError("NRF device is not connected.")
        


  