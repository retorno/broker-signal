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

from pathlib import Path
from contextlib import contextmanager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import os, time

present = EC.presence_of_element_located
invisible = EC.invisibility_of_element_located


def ID(value):
    return By.ID, value

def CLASS(value):
    return By.CLASS_NAME, value

def css(value):
    return By.CSS_SELECTOR, value

def xpath(value):
    return By.XPATH, value

def link_contains(value):
    return By.PARTIAL_LINK_TEXT, value

def js_href(el):
    return el.get_attribute('href').partition(':')[-1]


class WebDriver(webdriver.Chrome):
    env = None

    def __init__(self):
        if config.get("RUN_DOCKER"):
            time.sleep(2)
            print("###### => " + str(config))
            docker_host= config.get("SELENIUM_HUB")
            self.driver = webdriver.Remote(command_executor=docker_host, desired_capabilities=DesiredCapabilities.CHROME)
            self.wait = WebDriverWait(self.driver, 1)
            self.driver.set_page_load_timeout(9999)
            self.driver.implicitly_wait(3)
        else:
            options = webdriver.ChromeOptions()
            options.add_argument('--incognito')
            options.add_argument('--start-maximized')
            chromium_path = os.environ.get('DIR_LOCAL_DRIVER')
            download_dir = os.environ.get('DIR_LOCAL_DATA')        
            preferences = {"download.default_directory": download_dir}
            options.add_experimental_option("prefs", preferences)
            self.driver = super().__init__(executable_path= chromium_path, chrome_options=options)
            self.wait = WebDriverWait(self.driver, 1)
        
    def wait_until(self, method, timeout=20, interval=1):
        return WebDriverWait(self, timeout, interval).until(method)
    
    def element(self, locator):
        return self.find_element(*locator)

    @contextmanager
    def frame(self, name):
        self.switch_to.frame(name)
        yield
        self.switch_to.default_content()

    @contextmanager
    def tab(self):
        current = self.current_window_handle
        # open new tab
        self.execute_script('window.open("about:blank", "_blank");')
        # switch to new tab
        self.switch_to_window(self.window_handles[-1])
        yield
        # close tab
        self.close()
        # switch back to previous tab
        self.switch_to_window(current)

    def wait_downloads(self):
        self.get("chrome://downloads/")
        cmd = """
            var items = downloads.Manager.get().items_;
            if (items.every(e => e.state === "COMPLETE"))
                return items.map(e => e.file_path);     
        """
        # waits for all the files to be completed and returns the paths
        return self.wait_until(lambda d: d.execute_script(cmd), timeout=120)