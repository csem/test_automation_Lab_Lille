
from .macro import MACRO

import time
import numpy as np
import pyautogui
import os
from docx import Document
from pyppeteer import launch
import pyautogui
from pywinauto.application import Application
from time import sleep
from playwright.sync_api import sync_playwright



class Timeleads(MACRO):
    def start_playwright(self):
        self.playwright = sync_playwright().start()
        
        self.browser = self.playwright.chromium.launch(headless=False)
        self.page = self.browser.new_page()

    def close_playwright(self):
        self.browser.close()
        self.playwright.stop()

    def navigate(self, url):
        self.page.goto(url)
        sleep(5)

    def fill_form(self, frame, user_id, password):
        frame_element = self.page.query_selector('frame')
        frame = frame_element.content_frame()

        frame.fill('input[name="UserID"]', user_id)
        frame.fill('input[name="Password"]', password)
        sleep(2)

        with self.page.expect_navigation():
            frame.click('input[name="edit"]')

        sleep(6)

        frame_element = self.page.query_selector('frame')
        frame = frame_element.content_frame()

        return frame

    def interact_with_frames(self, frame_name,hours,minutes,description):
        frames = self.page.frames
        for frame in frames:
            print(frame.name)
            if frame.name == frame_name:
                frame.wait_for_selector('#hours')
                frame.select_option('#hours', hours)
                sleep(3)

                frame.wait_for_selector('#minutesList')
                frame.select_option('#minutesList', minutes)
                sleep(2)

                frame.wait_for_selector('#projList')
                frame.select_option('#projList', '6251798')
                sleep(2)

                frame.wait_for_selector('#description')
                frame.fill('#description', description)

                sleep(10)


        


  