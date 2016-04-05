#!/usr/bin/python

from __future__ import print_function
import os
import sys
import requests
import json
from framework import Framework
from utils import Utils
from settings import Settings
from marathonvalidator import MarathonValidator
from haproxyparser import HAProxyParser

utils = Utils()
settings = Settings()

class Marathon(Framework):

  def __init__(self):
    self.user = None
    self.passw = None
    self.marathonvalidator = MarathonValidator()
    self.haproxyparser = HAProxyParser() 

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

  def put(self, file_path, environmentObj, container, environment):
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

  def getGroupDetails(self, data):
    group_details = {}
    base_id = data['id']
    if not base_id.startswith("/"):
      base_id = "/" + base_id
    for group in data['groups']:
      if 'id' in group.keys():
        group_id = group['id']
        if not group_id.startswith("/"):
          group_id = "/" + group_id
        for app in group['apps']:
          http_prefix = ""
          tcp_port_value = ""
          tcp_port_list = []
          if 'id' in app.keys():
            app_id = app['id']
          if not app_id.startswith("/"):
            app_id = "/" + app_id
          container_id = "{}{}{}".format(base_id, group_id, app_id)
          if 'env' in app:
            if 'HTTP_PREFIX' in app['env']:
              http_prefix = app['env']['HTTP_PREFIX']

            if 'TCP_PORTS' in app['env']:
              tcp_ports_value = app['env']['TCP_PORTS']
              tcp_port_list = json.loads(tcp_ports_value).keys()

          envs = (http_prefix, tcp_port_list)
          group_details[container_id] = envs

    return group_details
    
  def validateGroupDetails(self, group_details):
    http_prefixes = {}
    tcp_ports = {}

    for app_id, detail in group_details.iteritems():
      http_prefix = detail[0]
      if (http_prefix in http_prefixes):
        print("HTTP_PREFIX conflict in Marathon template file. HTTP_PREFIX '{}' is used in multiple places.".format(http_prefix))
        return False
      else:
        if http_prefix != '':
          print("Prefix: {} app_id: {}".format(http_prefix, app_id))
          http_prefixes[http_prefix] = app_id

      tcp_port_list = detail[1]
      for tcp_port in tcp_port_list:
        if (tcp_port in tcp_ports) and (tcp_port != ''):
          print("TCP_PORT conflict in Marathon template file. TCP Port '{}' is used in multiple places.".format(tcp_port))
          return False
        else:
          tcp_ports[tcp_port] = app_id

    return True

  def runDeploymentChecks(self, file_path, environment):
    data = open(file_path).read()
    marathon_data = json.loads(data)
    if 'groups' in marathon_data:
      group_details = self.getGroupDetails(marathon_data)
      valid = self.validateGroupDetails(group_details)
      if valid == False:   # When there is a conflict among the apps in the template file
        return False
      else:
        app_ids = group_details.keys()
        for app_id in app_ids:
          result = self.marathonvalidator.validate(self.haproxyparser, environment, group_details[app_id][0], group_details[app_id][1], app_id)
          if result == False:
            print("Validation failed for app_id '{}'. Skipping push to Marathon.".format(app_id))
            return False
    else:
      app_id = marathon_data['id']
      if not app_id.startswith("/"):
        app_id = "/" + app_id
      http_prefix = ""
      tcp_port_list = []
      if 'env' in marathon_data:
        if 'HTTP_PREFIX' in marathon_data['env']:
          http_prefix = marathon_data['env']['HTTP_PREFIX']

        if 'TCP_PORTS' in marathon_data['env']:
          tcp_ports_value = marathon_data['env']['TCP_PORTS']
          tcp_port_list = json.loads(tcp_ports_value).keys()

      result = self.marathonvalidator.validate(self.haproxyparser, environment, http_prefix, tcp_port_list, app_id)
      if result == False:
        return False

    return True

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
