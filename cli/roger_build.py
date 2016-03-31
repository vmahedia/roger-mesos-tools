#!/usr/bin/python

from __future__ import print_function
import argparse
import json
import os
import sys
from settings import Settings
from appconfig import AppConfig

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
    return 'runs the docker build and optionally pushes it into the registry.'

def parse_args():
  parser = argparse.ArgumentParser(prog='roger build', description=describe())
  parser.add_argument('app_name', metavar='app_name',
    help="application to build. Example: 'agora'.")
  parser.add_argument('directory', metavar='directory',
    help="working directory. Example: '/home/vagrant/work_dir'.")
  parser.add_argument('tag_name', metavar='tag_name',
    help="tag for the built image. Example: 'roger-collectd:0.20'.")
  parser.add_argument('config_file', metavar='config_file',
    help="configuration file to use. Example: 'content.json'.")
  parser.add_argument('--push', '-p', help="Also push to registry. Defaults to false.", action="store_true")
  return parser

def main(settingObj, appObj, args):
  config_dir = settingObj.getConfigDir()
  root = settingObj.getCliDir()
  config = appObj.getConfig(config_dir, args.config_file)
  roger_env = appObj.getRogerEnv(config_dir)

  if 'registry' not in roger_env:
    print('Registry not found in roger-env.json file.')
    return 1

  if args.app_name not in config['apps']:
    print('Application specified not found.')
    return 1

  common_repo = config.get('repo', '')
  data = appObj.getAppData(config_dir, args.config_file, args.app_name)
  repo = ''
  if common_repo != '':
    repo = data.get('repo', common_repo)
  else:
    repo = data.get('repo', args.app_name)

  projects = data.get('privateProjects', ['none'])
  projects = ','.join(projects)
  docker_path = data.get('path', 'none')

  # get/update target source(s)
  file_exists = True
  file_path = ''
  cur_dir = ''
  if "PWD" in os.environ:
    cur_dir = os.environ.get('PWD')
  abs_path = os.path.abspath(args.directory)
  if docker_path != 'none':
    if abs_path == args.directory:
      file_path = "{0}/{1}/{2}".format(args.directory, repo, docker_path)
    else:
      file_path = "{0}/{1}/{2}/{3}".format(cur_dir, args.directory, repo, docker_path)
  else:
    if abs_path == args.directory:
      file_path = "{0}/{1}".format(args.directory, repo)
    else:
      file_path = "{0}/{1}/{2}".format(cur_dir, args.directory, repo)

  file_exists = os.path.exists("{0}/Dockerfile".format(file_path))

  if file_exists:
    image = "{0}/{1}".format(roger_env['registry'], args.tag_name)
    try:
      if abs_path == args.directory:
        exit_code = os.system("{0}/cli/docker_build.py '{1}' '{2}' '{3}' '{4}' '{5}'".format(root, args.directory, repo, projects, docker_path, image))
        if exit_code != 0:
          sys.exit('Docker build failed. Exiting from build.')
      else:
        exit_code = os.system("{0}/cli/docker_build.py '{1}/{2}' '{3}' '{4}' '{5}' '{6}'".format(root, cur_dir, args.directory, repo, projects, docker_path, image))
        if exit_code != 0:
          sys.exit('Docker build failed. Exiting from build.')
      build_message = "Image {0} built".format(image)
      if(args.push):
          exit_code = os.system("docker push {0}".format(image))
          if exit_code != 0:
            sys.exit('Docker push failed. Exiting from build.')
          build_message += " and pushed to registry {}".format(roger_env['registry'])
      print(build_message)
    except (IOError) as e:
      print("The folowing error occurred.(Error: %s).\n" % e, file=sys.stderr)
      sys.exit('Exiting from build.')
  else:
    print("Dockerfile does not exist in {0} dir:".format(file_path))

if __name__ == "__main__":
  settingObj = Settings()
  appObj = AppConfig()
  parser = parse_args()
  args = parser.parse_args()
  main(settingObj, appObj, args)
