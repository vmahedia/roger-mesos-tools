#!/usr/bin/python

from __future__ import print_function
import os
import sys
import requests
import json
from framework import Framework
from utils import Utils
from settings import Settings

utils = Utils()
settings = Settings()

class Marathon(Framework):

  def __init__(self):
    self.user = None
    self.passw = None

  def fetchUserPass(self, env):
    if self.user == None:
      self.user = settings.getUser()
    if self.passw == None:
      self.passw = settings.getPass(env)
    print("Using u:{}, p:****".format(self.user))

  def getName(self):
    return "Marathon"

  def get(self, roger_env, environment):
    url = roger_env['environments'][environment]['marathon_endpoint']+"/v2/apps"
    self.fetchUserPass(environment)
    resp = requests.get(url, auth=(self.user, self.passw))
    print ("Server response: [ {} - {} ]".format(resp.status_code, resp.reason))
    return resp.json()

  def put(self, file_path, environmentObj, container):
    data = open(file_path).read()
    appName = json.loads(data)['id']
    self.fetchUserPass(environment)
    print("TRIGGERING MARATHON FRAMEWORK UPDATE FOR: {}".format(container))
    resp = ""
    if 'groups' in data:
      resp = requests.put("{}/v2/groups/{}".format(environmentObj['marathon_endpoint'], appName),
            data=data,
            headers = {'Content-type': 'application/json'}, auth=(self.user, self.passw))
      print("curl -X PUT -H 'Content-type: application/json' --data-binary @{} {}/v2/groups/{}".format(file_path, environmentObj['marathon_endpoint'], appName))
      print ("Server response: [ {} - {} ]".format(resp.status_code, resp.reason))
    else:
      endpoint = environmentObj['marathon_endpoint']
      deploy_url = "{}/v2/apps/{}".format(endpoint, appName)
      resp = requests.put(deploy_url, data=data, headers = {'Content-type': 'application/json'}, auth=(self.user, self.passw))
      print("curl -X PUT -H 'Content-type: application/json' --data-binary @{} {}/v2/apps/{}".format(file_path, environmentObj['marathon_endpoint'], appName))
      print ("Server response: [ {} - {} ]".format(resp.status_code, resp.reason))

    marathon_message = "{0}: {1}".format(appName, resp)
    print(marathon_message)
    return resp

  def getCurrentImageVersion(self, roger_env, environment, application):
    data = self.get(roger_env, environment)
    self.fetchUserPass(environment)
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

  def getTasks(self, roger_env, environment):
    self.fetchUserPass(environment)
    headers = {'Accept': 'application/json','Accept-Encoding': 'gzip, deflate','Content-Type': 'application/json'}
    url = roger_env['environments'][environment]['marathon_endpoint']+'/v2/tasks?status=running'
    resp = requests.get("{}".format(url), headers=headers, auth=(self.user, self.passw))
    print ("Server response: [ {} - {} ]".format(resp.status_code, resp.reason))
    respjson = resp.json()
    tasks = resp.json()['tasks'] if 'tasks' in respjson else {}
    return tasks
