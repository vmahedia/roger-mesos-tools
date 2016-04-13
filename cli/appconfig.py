#!/usr/bin/python

from __future__ import print_function
import os
import os.path
import sys
import json
import yaml

class AppConfig:

  def getRogerEnv(self, config_dir):
    roger_env = None
    env_file = '{0}/roger-env.json'
    with open(env_file.format(config_dir)) as roger_env_file_obj:
      roger_env = yaml.load(roger_env_file_obj) if env_file.lower().endswith('.yml') else json.load(roger_env_file_obj)
    return roger_env

  def getConfig(self, config_dir, config_file):
    config = None
    if os.path.exists(config_file):
        with open(config_file) as config_file_obj:
          config = yaml.load(config_file_obj) if config_file.lower().endswith('.yml') else json.load(config_file_obj)
    else:
      with open('{0}/{1}'.format(config_dir, config_file)) as config_file_obj:
        config = yaml.load(config_file_obj) if config_file.lower().endswith('.yml') else json.load(config_file_obj)
    return config

  def getAppData(self, config_dir, config_file, app_name):
    config = self.getConfig(config_dir, config_file)
    app_data = ''
    if app_name in config['apps']:
      app_data = config['apps'][app_name]
    return app_data
