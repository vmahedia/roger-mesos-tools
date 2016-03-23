#!/usr/bin/python

from __future__ import print_function
import argparse
import json
import os
import sys
from settings import Settings
from appconfig import AppConfig
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

def main(object_list, args):
  settingObj = object_list[0]
  appObj = object_list[1]
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

  os.system("sudo pip install gitpython")
  from git import Repo
  git_url = "git@github.com:seomoz/{}.git".format(repo)
  # get/update target source(s)
  path = "{0}/{1}".format(args.directory, repo)
  try:
    repo = Repo.clone_from(git_url, path)
  except:
     if os.path.isdir(path):
       with chdir(path):
         os.system("git pull origin {}".format(branch))
     else:
       with chdir('{0}'.format(args.directory)):
         os.system("git clone --depth 1 --branch {} git@github.com:seomoz/{}.git".format(branch, repo))
         os.chdir(repo)

if __name__ == "__main__":
  settingObj = Settings()
  appObj = AppConfig()
  object_list = []
  object_list.append(settingObj)
  object_list.append(appObj)
  parser = parse_args()
  args = parser.parse_args()
  main(object_list, args)
