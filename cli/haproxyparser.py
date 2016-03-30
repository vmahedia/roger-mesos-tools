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

  http_prefixes = {}

  def get_haproxy_config(self, environment):
    haproxy_config = ""
    settingObj = Settings()
    appObj = AppConfig()
    config_dir = settingObj.getConfigDir()
    roger_env = appObj.getRogerEnv(config_dir)
    host = roger_env['environments'][environment]['host']
    haproxy_config_path = roger_env['environments'][environment]['haproxy_config_path']
    url = "{}{}".format(host, haproxy_config_path)
    print("Url: {}".format(url))
    haproxy_config = requests.get(url, stream=True) 
    return haproxy_config.text

  def parseConfig(self, environment):
    http_prefix_appids = {}
    config = self.get_haproxy_config(environment)
    aclrules = subprocess.check_output("echo \"{}\" | grep 'acl ::' ".format(config), shell=True)
    lines = aclrules.split('\n')
    for line in lines:
      pattern = re.compile("acl (.*)-aclrule path_beg -i (.*)")
      result = pattern.search(line)
      if result != None:
        app_id = result.group(1).replace("::","/")
        http_prefix = result.group(2)
        http_prefix_appids[http_prefix] = app_id
     
    self.set_http_prefixes(http_prefix_appids)

  def set_http_prefixes(self, http_prefix_appids):
    self.http_prefixes = http_prefix_appids

  def get_http_prefixes(self):
    return self.http_prefixes

'''
def main():
  haproxyObj = HAProxyParser()
  haproxyObj.parseConfig("dev")
  test_dict = haproxyObj.get_http_prefixes()

if __name__ == "__main__":
  main()
'''
