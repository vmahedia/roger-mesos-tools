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
from marathon import Marathon
from haproxyparser import HAProxyParser

def describe():
  return "provides details for running applications."

class RogerPS(object):

  def parse_args(self):
    parser = argparse.ArgumentParser(prog='roger ps', description=describe())
    parser.add_argument('-e', '--env', metavar='env', help="environment to search. Example: 'dev' or 'stage'")
    parser.add_argument('-v','--verbose', help="provides details for each instance of different running apps. Defaults to false.",  action="store_true")
    return parser

  def get_marathon_details(self, tasks, haproxyparser, environment, args):
    marathon_details = {}
    instances = {}
    instance_details = self.get_instance_details(tasks)
    for task_id in instance_details:
      app_id = instance_details[task_id][0]
      if app_id in instances.keys():
        tasks_list = instances[app_id]
        tasks_list.append(task_id)
        instances[app_id] = tasks_list
      else:
        tasks_list = []
        tasks_list.append(task_id)
        instances[app_id] = tasks_list

    haproxyparser.parseConfig(environment)
    http_prefixes = haproxyparser.get_path_begin_values()
    tcp_ports = haproxyparser.get_backend_tcp_ports()

    app_ids = {}
    for app_id in instances.keys():
      http_prefix = "None"
      tcp_port_list = []
      num_instances = len(instances[app_id])
      if app_id in http_prefixes.keys():
        http_prefix = http_prefixes[app_id]
      if app_id in tcp_ports.keys():
        tcp_port_list = tcp_ports[app_id]
      app_details = {}
      app_details["instances"] = num_instances
      app_details["http_prefix"] = http_prefix
      app_details["tcp_port_list"] = tcp_port_list
      if args.verbose:
        task_ids = {}
        for task_id in instances[app_id]: 
          task_details = {}
          task_details["hostname"] = instance_details[task_id][1]
          task_details["ports"] = instance_details[task_id][2]
          task_details["last_updated"] = instance_details[task_id][3]
          task_ids[task_id] = task_details
        app_details["tasks"] = task_ids
      app_ids[app_id] = app_details

    marathon_details["apps"] = app_ids
    return marathon_details

   
  def print_marathon_details(self, marathon_details, args):     
    print(json.dumps(marathon_details, indent=2))
 
    '''
    print("AppId\t\t\tNo of Instances\t\tHttp_Prefix\t\tTCP_Ports_List")
    for app_id in instances.keys():
      http_prefix = "None"
      tcp_port_list = []
      num_instances = len(instances[app_id])
      if app_id in http_prefixes.keys():
        http_prefix = http_prefixes[app_id]
      if app_id in tcp_ports.keys():
        tcp_port_list = tcp_ports[app_id]

      print("{}\t\t{}\t\t{}\t\t{}".format(app_id, num_instances, http_prefix, tcp_port_list))
      if args.verbose:
        print("       MesosTaskId\t\t\t\t\tHostname:[PortList]\t\t\t\tLast Updated")
        for task_id in instances[app_id]:
          print("    {}\t\t{}:{}\t\t{}".format(task_id, instance_details[task_id][1], instance_details[task_id][2], instance_details[task_id][3]))
    '''

  def get_instance_details(self, tasks):
    instance_details = {}
    for task in tasks:
      app_id = task['appId']
      started_at = task['startedAt']
      mesos_task_id = task['id']
      hostname = task['host']
      ports = task['ports']
      instance_details[mesos_task_id] = (app_id, hostname, ports, started_at)

    return instance_details
    

  def main(self, settings, appconfig, marathon, haproxyparser, args):
    config_dir = settings.getConfigDir()
    roger_env = appconfig.getRogerEnv(config_dir)
    environment = roger_env.get('default', '')

    if args.env is None:
      if "ROGER_ENV" in os.environ:
        env_var = os.environ.get('ROGER_ENV')
        if env_var.strip() == '':
          print("Environment variable $ROGER_ENV is not set.Using the default set from roger-env.json file")
        else:
          print("Using value {} from environment variable $ROGER_ENV".format(env_var))
          environment = env_var
    else:
      environment = args.env

    if environment not in roger_env['environments']:
      sys.exit('Environment not found in roger-env.json file.')

    tasks = marathon.getTasks(roger_env, environment)
    marathon_details = self.get_marathon_details(tasks, haproxyparser, environment, args)
    self.print_marathon_details(marathon_details, args)

  
if __name__ == '__main__':
  settings = Settings()
  appconfig = AppConfig()
  marathon = Marathon()
  haproxyparser = HAProxyParser()
  roger_ps = RogerPS()
  roger_ps.parser = roger_ps.parse_args()
  roger_ps.args = roger_ps.parser.parse_args()
  roger_ps.main(settings, appconfig, marathon, haproxyparser, roger_ps.args)
