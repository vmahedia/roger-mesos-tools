#!/usr/bin/python

from __future__ import print_function
import os
import sys
import requests
import json
from framework import Framework

class Marathon(Framework):

  def get(self, roger_env, environment):
    url = roger_env['environments'][environment]['marathon_endpoint']+"/v2/apps"
    resp = requests.get(url)
    return resp.json()

  def put(self, data, environmentObj, appName):
    endpoint = environmentObj['marathon_endpoint']
    deploy_url = "{}/v2/apps/{}".format(endpoint, appName)
    print(deploy_url)
    resp = requests.put(deploy_url, data=data, headers = {'Content-type': 'application/json'})
    return resp
