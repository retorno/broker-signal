#!/usr/bin/env python
# -*- coding: utf-8 -*-
from selenium.webdriver.support.ui import WebDriverWait
# import os
# import time
# from datetime import datetime
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
    # https://chrome.google.com/webstore/detail/always-clear-downloads/cpbmgiffkljiglnpdbljhlenaikojapc

    def __init__(self, config={}):
        options = webdriver.ChromeOptions()
        # options = Options()

        # options.add_argument('--kiosk')
        # options.add_argument('--start-maximized')
        # options.add_argument('--allow-running-insecure-content')
        # options.add_argument('--disable-web-security')
        # options.add_argument('--disk-cache-dir=/var/www/cake2.2.4/app/tmp/cache/selenium-chrome-cache')
        # options.add_argument('--no-referrers')
        # options.add_argument('--test-type')
        # options.add_argument('--window-size=1360,768')
        # options.add_argument('--disable-extensions')
        # options.add_argument('--proxy-server=localhost:8118')
        # options.add_argument("'chrome.prefs': {'profile.managed_default_content_settings.images': 2}")
        # options.add_argument('--dns-prefetch-disable')
        # options.add_argument('--ignore-certificate-errors')
        # if background:
        #    options.add_argument('--no-startup-window')
        options.add_argument('--incognito')

        chromium_path = os.environ.get('DIR_LOCAL_DRIVER')
        download_dir = os.environ.get('DIR_LOCAL_DATA')
        # options.binary_location = chromium_path
        
        preferences = {"download.default_directory": download_dir}
                    #    "download.prompt_for_download": False,
                    #    "download.directory_upgrade": True,
                    #    "safebrowsing.enabled": True }
        options.add_experimental_option("prefs", preferences)

        # import ipdb; ipdb.set_trace()
        self.driver = webdriver.Chrome(executable_path= chromium_path, chrome_options=options)
        # self.wait = WebDriverWait(self.driver, 1)
        # service_args=["--verbose", "--log-path=/Users/user/projects/routing-pack/lib/qc1.log"])
        # self.driver.execute_script("window.onblur = function() { window.onfocus() }")
        # self.driver.execute_script("window.onfocus = function onFocus() { document.body.className = 'focused' }")
        # self.driver.implicitly_wait(10)
        # self.driver.set_page_load_timeout(20)
        # self.driver.maximize_window()
        
        # else:  # docker 
        # time.sleep(2) # sleep to open conteiner selery + chrome
        # docker_host = os.environ.get('HOST_BROKER')
        # self.driver = webdriver.Remote(command_executor=docker_host, desired_capabilities=DesiredCapabilities.CHROME)
        # WebDriverWait(self.driver, 60)
        # self.driver.set_page_load_timeout(99999)
        # self.driver.implicitly_wait(60)