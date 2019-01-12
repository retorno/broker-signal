# -*- coding: utf-8 -*-
import re
import sys
import json
import yaml
import os
from os.path import basename, dirname, isfile


class Config(object):
    dir = None
    type = None
    conf = {}
    conf_file = None

    def __init__(self, conf_file=None):
        try:
            project_conf_file = os.getcwd() + "/config/conf.yml"
            if isfile(project_conf_file):
                stream = open(project_conf_file, "r")
                self.conf = yaml.load(stream)
                stream.close()

            if len(self.conf) == 0:
                raise NoConfig(project_conf_file + " or " + self.conf_file)

        except Exception as e:
            print(sys.stderr, str(e))


class NoConfig(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)