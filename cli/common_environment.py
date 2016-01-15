#!/usr/bin/env python

from __future__ import print_function
import argparse
import subprocess
import json
import os
import requests
import subprocess
import sys
from settings import Settings
from appconfig import AppConfig

class environment_parameters:

  def __init__(self):
      self.settingObj = Settings()
      self.appObj = AppConfig()

  @staticmethod
  def parse_args():
      parser = argparse.ArgumentParser(description='Get an Interactive Bash session into your container.')
      parser.add_argument('appTaskId', metavar='appTaskId', help="Application Task Id to uniquely \
	   identify a container Id. example: 'content.56847afe9799")
      parser.add_argument('-e', '--env', metavar='env', help="Environment to deploy to. \
	   example: 'dev' or 'stage'")
      parser.add_argument('-H','--hostname', metavar='hostname', help="Hostname to search.\
	    example: 'daldevmesos01' or 'daldevmesos04'")
      return parser

  @staticmethod
  def get_hostname_from_marathon(environment, roger_env, appTaskId):
      hostname = ''
      headers = {'Accept': 'application/json','Accept-Encoding': 'gzip, deflate','Content-Type': 'application/json'}
      url = roger_env['environments'][environment]['marathon_endpoint']+'/v2/tasks?status=running'
      resp = requests.get("{}".format(url), headers=headers)
      tasks = resp.json()['tasks']
      for task in tasks:
          if task['id'].startswith(appTaskId):
              hostname = task['host']

      return hostname

  @staticmethod
  def get_containerid(appTaskId, hostname):
      containerId = ''
      try:
          containers = subprocess.check_output("docker -H tcp://{}:4243 ps -q".format(hostname), shell=True)
      except:
          print("No route to host. Please check hostname '{}'".format(hostname), file=sys.stderr)
          return
      for container in containers.split('\n'):
          if container.strip() != '':
              try:
                  mesosTaskId = subprocess.check_output("docker -H tcp://{0}:4243 exec {1} \
                  printenv MESOS_TASK_ID".format(hostname,container), shell=True)
              except Exception as e:
                  print ("Ignoring exception: {}".format(str(e)))
                  pass
              if mesosTaskId:
                  if mesosTaskId.startswith(appTaskId):
                      containerId = container.strip()
                      break
              else:
                  print("Mesos Task Id info fetched is empty/blank for container id - {0}".format(container))
      return containerId
