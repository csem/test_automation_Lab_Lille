import crappy
import time
import pyvisa
import logging
from datetime import datetime
import inspect

class LoggerPerso():

    def __init__(self,class_name):
        self.class_nAME=class_name
        self.logger = logging.getLogger(class_name)
        self.logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler('mon_application.log')
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def __create_new_logger__(class_name):
        logger = logging.getLogger(class_name)
        logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler('mon_application.log')
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
      



