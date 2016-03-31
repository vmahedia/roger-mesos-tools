#!/usr/bin/env python

from __future__ import print_function
import os
import requests
import subprocess
import sys
import re
from appconfig import AppConfig
from settings import Settings

class HAProxyParser:

  path_begin_values = {}

  def get_haproxy_config(self, environment):
    haproxy_config = ""
    settingObj = Settings()
    appObj = AppConfig()
    config_dir = settingObj.getConfigDir()
    roger_env = appObj.getRogerEnv(config_dir)
    host = roger_env['environments'][environment]['host']
    haproxy_config_path = roger_env['environments'][environment]['haproxy_config_path']
    url = "{}{}".format(host, haproxy_config_path)
    haproxy_config = requests.get(url, stream=True) 
    return haproxy_config.text

  def parseConfig(self, environment):
    path_begin_values = {}
    config = self.get_haproxy_config(environment)
    aclrules = subprocess.check_output("echo \"{}\" | grep 'acl ::' ".format(config), shell=True)
    lines = aclrules.split('\n')
    for line in lines:
      pattern = re.compile("acl (.*)-aclrule path_beg -i (.*)")
      result = pattern.search(line)
      if result != None:
        acl_name = result.group(1).replace("::","/")
        path_begin_value = result.group(2)
        path_begin_values[path_begin_value] = acl_name
     
    self.set_path_begin_values(path_begin_values)

  def set_path_begin_values(self, path_begin_values_aclnames):
    self.path_begin_values = path_begin_values_aclnames

  def get_path_begin_values(self):
    return self.path_begin_values
