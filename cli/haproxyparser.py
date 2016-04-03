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
  backend_services_tcp_ports = {}

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
    backend_tcp_ports = {}
    config = self.get_haproxy_config(environment)

    aclrules = subprocess.check_output("echo \"{}\" | grep 'acl ::' ".format(config), shell=True)
    backend_service_names = subprocess.check_output("echo \"{}\" | grep 'listen ::' ".format(config), shell=True)
    lines = aclrules.split('\n')
    for line in lines:
      pattern = re.compile("acl (.*)-aclrule path_beg -i (.*)")
      result = pattern.search(line)
      if result != None:
        acl_name = result.group(1).replace("::","/")
        path_begin_value = result.group(2)
        path_begin_values[path_begin_value] = acl_name

    lines = backend_service_names.split('\n')
    for line in lines:
      if not line.startswith('#'):
        pattern = re.compile("listen (.*)-cluster-tcp-(.*) :(.*)")
        result = pattern.search(line)
        if result != None:
          backend_service_name = result.group(1).replace("::","/")
          tcp_port = result.group(3)
          backend_tcp_ports[tcp_port] = backend_service_name
     
    self.set_path_begin_values(path_begin_values)
    self.set_backend_tcp_ports(backend_tcp_ports)

  def set_path_begin_values(self, path_begin_values_aclnames):
    self.path_begin_values = path_begin_values_aclnames

  def get_path_begin_values(self):
    return self.path_begin_values

  def set_backend_tcp_ports(self, backend_services_tcp_ports):
    self.backend_services_tcp_ports = backend_services_tcp_ports

  def get_backend_tcp_ports(self):
    return self.backend_services_tcp_ports
