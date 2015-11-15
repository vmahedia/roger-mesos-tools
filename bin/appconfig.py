#!/usr/bin/python

from __future__ import print_function
import os
import sys
import json

class AppConfig:

  def getRogerEnvObject(self, config_dir):
    with open('{0}/roger-env.json'.format(config_dir)) as roger_env:
      roger_env = json.load(roger_env)
    return roger_env

  def getConfigObject(self, config_dir, config_file):
    with open('{0}/{1}'.format(config_dir, config_file)) as config:
      config = json.load(config)
    return config

  def getAppObject(self, config_dir, config_file, app_name):
    config = self.getConfigObject(config_dir, config_file)
    app_data = ''
    if app_name in config['apps']:
      app_data = config['apps'][app_name]
    return app_data
