#!/usr/bin/python

from __future__ import print_function
import os
import sys
import requests
import json
from framework import Framework
from utils import Utils
utils = Utils()

class Marathon(Framework):

  def getName(self):
    return "Marathon"

  def get(self, roger_env, environment):
    url = roger_env['environments'][environment]['marathon_endpoint']+"/v2/apps"
    resp = requests.get(url)
    return resp.json()

  def put(self, file_path, environmentObj, container):
    data = open(file_path).read()
    appName = json.loads(data)['id']
    print("TRIGGERING MARATHON FRAMEWORK UPDATE FOR: {}".format(container))
    resp = ""
    if 'groups' in data:
      resp = requests.put("{}/v2/groups/{}".format(environmentObj['marathon_endpoint'], appName),
            data=data,
            headers = {'Content-type': 'application/json'})
      print("curl -X PUT -H 'Content-type: application/json' --data-binary @{} {}/v2/groups/{}".format(file_path, environmentObj['marathon_endpoint'], appName))
    else:
      print("curl -X PUT -H 'Content-type: application/json' --data-binary @{} {}/v2/apps/{}".format(file_path, environmentObj['marathon_endpoint'], appName))
      endpoint = environmentObj['marathon_endpoint']
      deploy_url = "{}/v2/apps/{}".format(endpoint, appName)
      resp = requests.put(deploy_url, data=data, headers = {'Content-type': 'application/json'})

    marathon_message = "{0}: {1}".format(appName, resp)
    print(marathon_message)
    return resp

  def getCurrentImageVersion(self, roger_env, environment, application):
    data = self.get(roger_env, environment)
    for app in data['apps']:
      if app['container'] != None:
        docker_image = app['container']['docker']['image']
        if application in docker_image:
          if len(docker_image.split('/v')) == 2:
            #Image format expected moz-content-kairos-7da406eb9e8937875e0548ae1149/v0.46
            return utils.extractFullShaAndVersion(docker_image)
          else:
            #Docker images of the format: grafana/grafana:2.1.3 or postgres:9.4.1 
            return docker_image

