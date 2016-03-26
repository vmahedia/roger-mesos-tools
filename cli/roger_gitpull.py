#!/usr/bin/python

from __future__ import print_function
import argparse
import json
import os
import sys
from settings import Settings
from appconfig import AppConfig
from gitutils  import GitUtils
import errno

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
  return 'pulls code from the application git repository (clones the repository).'

def parse_args():
  parser = argparse.ArgumentParser(prog='roger gitpull', description=describe())
  parser.add_argument('app_name', metavar='app_name',
    help="application for which code is to be pulled. Example: 'agora' or 'grafana'")
  parser.add_argument('directory', metavar='directory',
    help="working directory. The repo has its own directory it this. Example: '/home/vagrant/work_dir'")
  parser.add_argument('-b', '--branch', metavar='branch',
    help="git branch to pull code from. Example: 'production' or 'master'. Defaults to master.")
  parser.add_argument('config_file', metavar='config_file',
    help="configuration file to use. Example: 'content.json' or 'kwe.json'")
  return parser

def main(settings, appConfig, gitObject, args):
  settingObj = settings
  appObj = appConfig
  gitObj = gitObject
  config_dir = settingObj.getConfigDir()
  config = appObj.getConfig(config_dir, args.config_file)

  if args.app_name not in config['apps']:
    sys.exit('Application specified not found.')

  common_repo = config.get('repo', '')
  data = appObj.getAppData(config_dir, args.config_file, args.app_name)
  repo = ''
  if common_repo != '':
    repo = data.get('repo', common_repo)
  else:
    repo = data.get('repo', args.app_name)

  branch = "master"	#master by default
  if not args.branch is None:
    branch = args.branch

  if not os.path.exists(args.directory):
    try:
        os.makedirs(args.directory)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
  # get/update target source(s)
  path = "{0}/{1}".format(args.directory, repo)
  if os.path.isdir(path):
    with chdir(path):
      gitObj.gitPull(branch)
  else:
    with chdir('{0}'.format(args.directory)):
      gitObj.gitShallowClone(repo, branch)

if __name__ == "__main__":
  settingObj = Settings()
  appObj = AppConfig()
  gitObj = GitUtils()
  parser = parse_args()
  args = parser.parse_args()
  main(settingObj, appObj, gitObj, args)
