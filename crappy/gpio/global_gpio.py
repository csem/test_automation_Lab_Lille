import RPi.GPIO as gpio_module
from .gpio import GPIO

class GlobalGPIO(GPIO):

    def __init__(self, pin):
        self.pin = pin
        gpio_module.setmode(gpio_module.BCM)
        gpio_module.setup(self.pin, gpio_module.OUT)

    def turn_on(self):
        gpio_module.output(self.pin, gpio_module.HIGH)

    def turn_off(self):
        gpio_module.output(self.pin, gpio_module.LOW)

    def toggle(self):
        if gpio_module.input(self.pin):
            self.turn_off()
        else:
            self.turn_on()

    def blink(self, duration=1, frequency=1):
        interval = 1.0 / (2 * frequency) 
        end_time = time.time() + duration
        while time.time() < end_time:
            self.toggle()
            time.sleep(interval)

    def cleanup(self):
        gpio_module.cleanup(self.pin)