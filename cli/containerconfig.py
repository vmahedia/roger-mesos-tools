#!/usr/bin/env python

from __future__ import print_function
import argparse
import subprocess
import json
import os
import requests
import subprocess
import sys

class ContainerConfig:

  def get_hostname_from_marathon(self, environment, roger_env, appTaskId):
    hostname = ''
    headers = {'Accept': 'application/json','Accept-Encoding': 'gzip, deflate','Content-Type': 'application/json'}
    url = roger_env['environments'][environment]['marathon_endpoint']+'/v2/tasks?status=running'
    resp = requests.get("{}".format(url), headers=headers)
    tasks = resp.json()['tasks']
    for task in tasks:
      if task['id'].startswith(appTaskId):
        hostname = task['host']

    return hostname

  def get_containerid(self, appTaskId, hostname):
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
