#!/usr/bin/env python
from selenium import webdriver
import json


class WebDriver(object):
    def __init__(self):
        config = json.loads(open('config/env.json').read())
        options = webdriver.ChromeOptions()
        options.add_argument('--incognito')
        chromium_path = config["DIR_LOCAL_DRIVER"]
        download_dir = config["DIR_LOCAL_DATA"]
        preferences = {"download.default_directory": download_dir}
        options.add_experimental_option("prefs", preferences)
        self.driver = webdriver.Chrome(executable_path=chromium_path, chrome_options=options)
