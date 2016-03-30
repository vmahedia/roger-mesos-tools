#!/usr/bin/python

from __future__ import print_function
import argparse
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import requests
import json
import os
import sys
import traceback
import logging
from settings import Settings
from appconfig import AppConfig
from marathon import Marathon
from chronos import Chronos
from frameworkUtils import FrameworkUtils

import contextlib

@contextlib.contextmanager
def chdir(dirname):
  '''Withable chdir function that restores directory'''
  curdir = os.getcwd()
  try:
    os.chdir(dirname)
    yield
  finally: os.chdir(curdir)

def describe():
  return 'pushes the application into roger mesos.'

def parse_args():
  parser = argparse.ArgumentParser(prog='roger push', description=describe())
  parser.add_argument('app_name', metavar='app_name',
    help="application to push. Example: 'agora' or 'grafana'")
  parser.add_argument('-e', '--env', metavar='env',
    help="environment to push to. Example: 'dev' or 'prod'")
  parser.add_argument('directory', metavar='directory',
    help="working directory. Example: '/home/vagrant/work_dir'")
  parser.add_argument('image_name', metavar='image_name',
    help="image name that includes version to use. Example: 'roger-collectd-v0.20' or 'elasticsearch-v0.07'")
  parser.add_argument('config_file', metavar='config_file',
    help="configuration file to use. Example: 'content.json' or 'kwe.json'")
  parser.add_argument('--skip-push', '-s', help="skips push. Only generates components for review. Defaults to false.", action="store_true")
  parser.add_argument('--force-push', '-f', help="force push. Forces push even if validation checks failed. Defaults to false.", action="store_true")
  parser.add_argument('--secrets-file', '-S',
    help="specifies an optional secrets file for deploy runtime variables.")
  return parser

def loadSecretsJson(secrets_dir, json_file_name, args, environment):
  if args.secrets_file is not None:
    print("Using specified secrets file: {}".format(args.secrets_file))
    json_file_name = args.secrets_file
  exists = os.path.exists(secrets_dir)
  if exists == False:
   os.makedirs(secrets_dir)

  # Two possible paths -- first without environment, second with
  path1 = "{}/{}".format(secrets_dir, json_file_name)
  path2 = "{}/{}/{}".format(secrets_dir, environment, json_file_name)
  print(" Loading secrets from {} or {}".format(path1, path2))

  try:
    with open(path1) as f:
      return json.load(f)
  except IOError:
    pass

  try:
    with open(path2) as f:
      return json.load(f)
  except IOError:
    print(" Couldn't load secrets file environment in %s or %s\n" % (path1, path2), file=sys.stderr)
    return {}

def replaceSecrets(output_dict, secrets_dict):
  if type(output_dict) is not dict:
    return output_dict

  for key in output_dict:
    if output_dict[key] == "SECRET":
      if key in secrets_dict.keys():
        output_dict[key] = secrets_dict[key]

    if type(output_dict[key]) is list:
      temp_list = []
      for list_elem in output_dict[key]:
        temp_list.append(replaceSecrets(list_elem, secrets_dict))
        output_dict[key] = temp_list

    if type(output_dict[key]) is dict:
      temp_dict = replaceSecrets(output_dict[key], secrets_dict)
      output_dict[key] = temp_dict

  return output_dict

def mergeSecrets(json_str, secrets):
  '''Given a JSON string and an object of secret environment variables, replaces
  parses the JSON keys with the secret variables. Returns back
  a JSON string. Raises an error if there are any SECRET variables still exists.'''
  output_dict = json.loads(json_str)
  json_str = json.dumps(replaceSecrets(output_dict, secrets), indent=4)

  if '\"SECRET\"' in json_str:
      raise StandardError('There are still "SECRET" values -- does your secrets file have all secret environment variables?')
  return json_str

def renderTemplate(template, environment, image, app_data, config, container):
    output = ''
    variables = {}
    variables['environment'] = environment
    variables['image'] = image

    #Adding Global and environment variables for all apps
    if 'vars' in config:
      if 'global' in config['vars']:
        for global_var in config['vars']['global']:
          variables[global_var] = config['vars']['global'][global_var]

      if 'environment' in config['vars']:
        if environment in config['vars']['environment']:
          for env_var in config['vars']['environment'][environment]:
            variables[env_var] = config['vars']['environment'][environment][env_var]

    #Adding Global and environment variables for specific app.
    #If the same variable is already present in "variables" dictonary,it will get overriden
    if 'vars' in app_data:
      if 'global' in app_data['vars']:
        for global_var in app_data['vars']['global']:
          variables[global_var] = app_data['vars']['global'][global_var]

      if 'environment' in app_data['vars']:
        if environment in app_data['vars']['environment']:
          for env_var in app_data['vars']['environment'][environment]:
            variables[env_var] = app_data['vars']['environment'][environment][env_var]

    if type(container) == dict:
      if 'vars' in container:
        container_vars = container['vars']
        if 'global' in container_vars:
          for global_var in container_vars['global']:
            variables[global_var] = container_vars['global'][global_var]
        if 'environment' in container_vars:
          if environment in container_vars['environment']:
            for env_var in container_vars['environment'][environment]:
              variables[env_var] = container_vars['environment'][environment][env_var]

    output = template.render(variables)
    return output

def main(settings, appConfig, frameworkObject, args):
  settingObj = settings
  appObj = appConfig
  frameworkUtils = frameworkObject
  config_dir = settingObj.getConfigDir()

  cur_file_path = os.path.dirname(os.path.realpath(__file__))
  config = appObj.getConfig(config_dir, args.config_file)
  roger_env = appObj.getRogerEnv(config_dir)

  if 'registry' not in roger_env.keys():
    print('Registry not found in roger-env.json file.Exiting...')
    return 1

  if args.app_name not in config['apps'].keys():
    print('Application specified not found.Exiting...')
    return 1

  environment = roger_env.get('default', '')
  if args.env is None:
    if "ROGER_ENV" in os.environ:
      env_var = os.environ.get('ROGER_ENV')
      if env_var.strip() == '':
        print("Environment variable $ROGER_ENV is not set. Using the default set from roger-env.json file")
      else:
        print("Using value {} from environment variable $ROGER_ENV".format(env_var))
        environment = env_var
  else:
    environment = args.env

  if environment not in roger_env['environments']:
    print('Environment not found in roger-env.json file.Exiting...')
    return 1

  environmentObj = roger_env['environments'][environment]
  common_repo = config.get('repo', '')
  data = appObj.getAppData(config_dir, args.config_file, args.app_name)
  frameworkObj = frameworkUtils.getFramework(data)
  framework = frameworkObj.getName()

  repo = ''
  if common_repo != '':
    repo = data.get('repo', common_repo)
  else:
    repo = data.get('repo', args.app_name)

  comp_dir = settingObj.getComponentsDir()
  templ_dir = settingObj.getTemplatesDir()
  secrets_dir = settingObj.getSecretsDir()

  # template marathon files
  data_containers = data['containers']

  for container in data_containers:
    if type(container) == dict:
       container_name = str(container.keys()[0])
       container = container[container_name]
       containerConfig = "{0}-{1}.json".format(config['name'], container_name)
    else:
       container_name = container
       containerConfig = "{0}-{1}.json".format(config['name'], container)

    template = ''
    os.chdir(cur_file_path) #  Required for when work_dir,component_dir,template_dir or secret_env_dir is something like '.' or './temp"
    app_path = ''
    if 'template_path' not in data:
      app_path = templ_dir
    else:
      cur_dir = ''
      if "PWD" in os.environ:
        cur_dir = os.environ.get('PWD')
      abs_path = os.path.abspath(args.directory)
      if abs_path == args.directory:
        app_path = "{0}/{1}/{2}".format(args.directory, repo, data['template_path'])
      else:
        app_path = "{0}/{1}/{2}/{3}".format(cur_dir, args.directory, repo, data['template_path'])

    if not app_path.endswith('/'):
        app_path = app_path + '/'

    env = Environment(loader=FileSystemLoader("{}".format(app_path)))
    template = env.get_template(containerConfig)
    image_path = "{0}/{1}".format(roger_env['registry'], args.image_name)
    print("Rendering content from template [{}{}] for environment [{}]".format(app_path, containerConfig, environment))
    output = renderTemplate(template, environment, image_path, data, config, container)
    #Adding check so that not all apps try to mergeSecrets
    outputObj = json.loads(output)
    if 'SECRET' in output:
      output = mergeSecrets(output, loadSecretsJson(secrets_dir, containerConfig, args, environment))

    try:
      comp_exists = os.path.exists("{0}".format(comp_dir))
      if comp_exists == False:
        os.makedirs("{0}".format(comp_dir))
      comp_env_exists = os.path.exists("{0}/{1}".format(comp_dir, environment))
      if comp_env_exists == False:
        os.makedirs("{0}/{1}".format(comp_dir, environment))
    except Exception as e:
      logging.error(traceback.format_exc())
    with open("{0}/{1}/{2}".format(comp_dir, environment, containerConfig), 'wb') as fh:
      fh.write(output)

  if args.skip_push:
      print("Skipping push to {} framework. The rendered config file(s) are under {}/{}".format(framework, comp_dir, environment))
  else:
      # push to roger framework
      for container in data_containers:
        if type(container) == dict:
           container_name = str(container.keys()[0])
           containerConfig = "{0}-{1}.json".format(config['name'], container_name)
        else:
          container_name = container
          containerConfig = "{0}-{1}.json".format(config['name'], container)

        config_file_path = "{0}/{1}/{2}".format(comp_dir, environment, containerConfig)

        result = frameworkObj.runDeploymentChecks(config_file_path, environment)
        if args.force_push or result == True: 
          frameworkObj.put(config_file_path, environmentObj, container_name, environment)
        else:
          print("Skipping push to {} framework for container {} as Validation Checks failed.".format(framework, container))

if __name__ == "__main__":
  settingObj = Settings()
  appObj = AppConfig()
  frameworkUtils = FrameworkUtils()
  parser = parse_args()
  args = parser.parse_args()
  main(settingObj, appObj, frameworkUtils, args)
