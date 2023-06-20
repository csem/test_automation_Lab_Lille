

from .jlink import JLINK
from pynrfjprog import API, HighLevel,LowLevel
import pylink


class Global_JLINK(JLINK):
    def start_rtt(self):
        if self.connected:
            self.api.rtt_start()
            self.rtt = True
        else:
            raise RuntimeError("NRF device is not connected.")
    def get_data(self):
        if self.connected:
            data = None
            return data
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
            return self.api.rtt_read(up_channel_index, length)
        else:
            raise RuntimeError("NRF device is not connected.")

    def write_rtt(self, down_channel_index=0, data=None):
        if self.connected and self.rtt and data is not None:
            return self.api.rtt_write(down_channel_index, data)
        else:
            raise RuntimeError("NRF device is not connected.")

    def start_stream(self):
        if self.connected:
            pass
        else:
            raise RuntimeError("NRF device is not connected.")

    def get_stream(self):
        if self.connected:
            stream_data = None
            return stream_data
        else:
            raise RuntimeError("NRF device is not connected.")

    def stop_stream(self):
        if self.connected:
            pass
        else:
            raise RuntimeError("NRF device is not connected.")
        
    def read_data(self, addr, data_len):
        if self.connected:
            return self.api.read(addr, data_len)
        else:
            raise RuntimeError("NRF device is not connected.")
    
    def flash_firmware(self, firmware_path):
        if self.connected:
            try:
                self.api.sys_reset()
                self.api.erase_all()
                self.api.program_file(firmware_path)
                self.api.sys_reset()
                self.api.go()
                return True
            except Exception as e:
                return False
        else:
            raise RuntimeError("NRF device is not connected.")