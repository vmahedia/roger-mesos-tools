#!/usr/bin/python

from __future__ import print_function
import argparse
import json
import os
import sys
from settings import Settings

import contextlib

@contextlib.contextmanager
def chdir(dirname):
  '''Withable chdir function that restores directory'''
  curdir = os.getcwd()
  try:
    os.chdir(dirname)
    yield
  finally: os.chdir(curdir)

def parse_args():
  parser = argparse.ArgumentParser(description='Creates an initial application template and a project config file.')
  parser.add_argument('app_name', metavar='app_name',
    help="An application name unique within a project (or team). Examples: 'grafana', 'agora', 'crux:web'")
  parser.add_argument('project_name', metavar='project_name',
    help="A project (or team) name. Examples: 'roger', 'content', 'kwe'")
  parser.add_argument('-f', '--framework',
    help="Framework to deploy to the application. Defaults to marathon.'")
  return parser

def writeJson(json, path, filename):
  exists = os.path.exists(os.path.abspath(path))
  if exists == False:
    os.makedirs(path)
  with open("{0}/{1}".format(path, filename), 'wb') as fh:
      fh.write(json)

def createSlackTags():
  slack_dict = {}
  slack_dict['channel'] = "channel_id"
  slack_dict['method'] = "chat.postMessage"
  slack_dict['username'] = "project_name Deployment"
  slack_dict['emoji'] = ":rocket:"
  return slack_dict

def createVariableTags():
  variables, global_dict, environment, dev_dict, stage_dict, prod_dict = [{} for dummy in range(6)]
  environment['dev'] = dev_dict
  environment['stage'] = stage_dict
  environment['prod'] = prod_dict
  variables['global'] = global_dict
  variables['environment'] = environment
  return variables

def createAppTags(app_name, framework):
  app_dict, details = {}, {}
  details['name'] = app_name
  details['template_path'] = "framework_template_path"
  details['path'] = "dockerfile_path"
  details['vars'] = createVariableTags()
  if not framework is None:
    details['framework'] = "{0}".format(framework)
  container_list = ['{0}'.format(app_name)]
  details['containers'] = container_list
  app_dict['{0}'.format(app_name)] = details
  return app_dict

def createAppConfig(config_dir, filename, app_name, project_name, framework):
  path = "{0}".format(config_dir)
  json_dict, app_dict = {}, {}
  json_dict['name'] = project_name
  json_dict['notifications'] = createSlackTags()
  json_dict['repo'] = "repo_name"
  json_dict['vars'] = createVariableTags()
  app_dict = createAppTags(app_name, framework)
  json_dict['apps'] = app_dict
  json_output = json.dumps(json_dict, indent=2)
  path = "{0}".format(config_dir)
  writeJson(json_output, path, filename)

def createPortMappings():
  port_dict = {}
  port_dict['containerPort'] = 8125
  port_dict['hostPort'] = 0
  port_dict['servicePort'] = 0
  port_dict['protocol'] = "tcp"
  return port_dict

def createContainerTags():
  container_dict, docker_dict = {}, {}
  docker_dict['image'] = "{{ image }}"
  docker_dict['network'] = "BRIDGE"
  port_mappings = []
  port_mappings.append(createPortMappings())
  docker_dict['portMappings'] = port_mappings
  container_dict['type'] = "DOCKER"
  container_dict['docker'] = docker_dict
  return container_dict

def createMarathonConfig(templ_dir, filename, app_id):
  json_dict, env = {}, {}
  json_dict['container'] = createContainerTags()
  env['ENV_VAR1'] = "value1"
  env['ENV_VAR2'] = "value2"
  json_dict['id'] = app_id
  json_dict['instances'] = "1"
  json_dict['cpus'] = "0.2"
  json_dict['mem'] = "1"
  json_dict['env'] = env
  json_output = json.dumps(json_dict, indent=2)
  writeJson(json_output, templ_dir, filename)

def main():
  parser = parse_args()
  args = parser.parse_args()
  config_dir = settingObj.getConfigDir()

  templ_dir = settingObj.getTemplatesDir()
  config_file = "{0}.json".format(args.project_name)
  file_exists = os.path.exists("{0}/{1}".format(config_dir, config_file))

  if file_exists:
    print("File {0} already exists in {1}/".format(config_file, config_dir))
  else:
    createAppConfig(config_dir, config_file, args.app_name, args.project_name, args.framework)
    print("Sample {0} application file {1} created under {2}/".format(args.app_name, config_file, config_dir))

  framework_filename = "{0}-{1}.json".format(args.project_name, args.app_name)
  file_exists = os.path.exists("{0}/{1}".format(templ_dir, framework_filename))
  if file_exists:
    print("File {0} already exists in {1}".format(framework_filename, templ_dir))
  else:
    app_id = "{0}-{1}".format(args.project_name, args.app_name)
    createMarathonConfig(templ_dir, framework_filename, app_id)
    print("Sample Marathon file {0} created under {1}".format(framework_filename, templ_dir))

if __name__ == "__main__":
  settingObj = Settings()
  main()
