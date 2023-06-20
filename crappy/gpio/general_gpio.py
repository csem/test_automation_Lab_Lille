import RPi.GPIO as GPIO

from .gpio import GPIO
from ..general_class import LoggerPerso


class General_GPIO(GPIO,LoggerPerso):
    def __init__(self, pin_number, mode=GPIO.BCM):
        self.pin_number = pin_number
        self.mode = mode

        # Initialiser les broches GPIO
        GPIO.setmode(self.mode)
        GPIO.setup(self.pin_number, GPIO.OUT)

    def set_high(self):
        GPIO.output(self.pin_number, GPIO.HIGH)

    def set_low(self):
        GPIO.output(self.pin_number, GPIO.LOW)

    def toggle(self):
        current_state = GPIO.input(self.pin_number)
        new_state = GPIO.LOW if current_state == GPIO.HIGH else GPIO.HIGH
        GPIO.output(self.pin_number, new_state)

    def cleanup(self):
        GPIO.cleanup(self.pin_number)