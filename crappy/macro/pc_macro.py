
from .macro import MACRO

import time
import numpy as np
import pyautogui
import os
from docx import Document

class PC_MACRO(MACRO):

    def __init__(self):
        self.gui=pyautogui

    def word_open(self):
        self.gui.press('win')
        time.sleep(0.5)
        self.gui.write('Word')
        self.gui.press('enter')
        time.sleep(5)

    def word_new_page(self):
        self.gui.press('enter')
        time.sleep(0.5)
    
    def word_write_text(self,content):
        self.gui.write(content)
        time.sleep(0.5)

    def word_save_file(self,filename):
        time.sleep(0.5)
        self.gui.hotkey("alt","f")
        time.sleep(0.5)
        self.gui.press("U")
        time.sleep(1)
        self.gui.press("O")
        time.sleep(1)
        path = os.getcwd() + "\\" + filename+".docx"
        pyautogui.write(path)
        time.sleep(1)
        pyautogui.press('enter')
    
        time.sleep(1)
        pyautogui.press('enter')

    def word_get_content(self,filename):
        doc = Document(filename)
        for para in doc.paragraphs:
            text = para.text.replace('\xa0', ' ')
            return text
        
    def word_close(self):
        time.sleep(1)
        self.gui.hotkey('alt', 'f4')
        time.sleep(1)
    
        


        


  