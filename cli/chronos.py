#!/usr/bin/python

from __future__ import print_function
import os
import sys
import requests
import json
from framework import Framework

class Chronos(Framework):

  def get(self, roger_env, environment):
    url = roger_env['environments'][environment]['chronos_endpoint']+"/scheduler/jobs"
    resp = requests.get(url)
    return resp.json()

  def put(self, data, environmentObj, appName):
    endpoint = environmentObj['chronos_endpoint']
    deploy_url = "{}/scheduler/iso8601".format(endpoint)
    print(deploy_url)
    resp = requests.put(deploy_url, data=data, headers = {'Content-type': 'application/json'})
    return resp
