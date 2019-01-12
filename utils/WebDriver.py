#!/usr/bin/env python
# -*- coding: utf-8 -*-
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver

from selenium.webdriver.common.keys import Keys
import selenium.webdriver.chrome.service as service
import unicodedata
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
import os, time


class WebDriver(object):
    env = None

    def __init__(self, *args, **kwargs):
        if self.env.get("RUN_DOCKER"):
            time.sleep(2)
            docker_host= self.env.get("SELENIUM_HUB")
            self.driver = webdriver.Remote(command_executor=docker_host, desired_capabilities=DesiredCapabilities.CHROME)
            self.wait = WebDriverWait(self.driver, 1)
            self.driver.set_page_load_timeout(9999)
            self.driver.implicitly_wait(3)
        else:
            options = webdriver.ChromeOptions()
            options.add_argument('--incognito')
            chromium_path = os.environ.get('DIR_LOCAL_DRIVER')
            download_dir = os.environ.get('DIR_LOCAL_DATA')        
            preferences = {"download.default_directory": download_dir}
            options.add_experimental_option("prefs", preferences)
            self.driver = webdriver.Chrome(executable_path= chromium_path, chrome_options=options)
            self.wait = WebDriverWait(self.driver, 1)
        
