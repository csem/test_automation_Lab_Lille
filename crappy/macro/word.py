
from .macro import MACRO

import time
import numpy as np
import pyautogui
import os
from docx import Document
from pyppeteer import launch
import pyautogui
from time import sleep
from playwright.sync_api import sync_playwright



class Word(MACRO):

    def word_open(self):
        self.press_keys('win')
        sleep(0.5)
        self.write_keys('Word')
        self.press_keys('enter')
        sleep(8)

    def word_new_page(self):
        self.press_keys('enter')
        sleep(0.5)
    
    def word_write_text(self,content):
        self.write_keys(content)
        sleep(0.5)

    def word_save_file(self,filename):
        sleep(0.5)
        self.press_hotkeys(["alt","f"])
        sleep(0.5)
        self.press_keys("U")
        sleep(1)
        self.press_keys("O")
        sleep(1)
        path = os.getcwd() + "\\" + filename+".docx"
        self.write_keys(path)
        sleep(1)
        self.press_keys('enter')
    
        sleep(1)
        self.press_keys('enter')
        sleep(0.5)




    def word_get_content(self,filename):
        doc = Document(filename)
        for para in doc.paragraphs:
            text = para.text.replace('\xa0', ' ')
            return text
        
    def word_close(self):
        sleep(1)
        self.press_hotkeys(['alt', 'f4'])
        sleep(1)
        self.press_keys('enter')
        sleep(0.5)
    



  