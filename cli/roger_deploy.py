#!/usr/bin/python

from __future__ import print_function
from tempfile import mkdtemp
import argparse
from decimal import *
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import subprocess
import json
import os
import requests
import sys
import roger_gitpull
import re
import shutil
from settings import Settings
from appconfig import AppConfig
from marathon import Marathon
from chronos import Chronos
from frameworkUtils import FrameworkUtils
from gitutils  import GitUtils

import contextlib

@contextlib.contextmanager
def chdir(dirname):
  '''Withable chdir function that restores directory'''
  curdir = os.getcwd()
  try:
    os.chdir(dirname)
    yield
  finally: os.chdir(curdir)

#To remove a temporary directory created by roger-deploy if this script exits
def removeDirTree(work_dir, args):
  exists = os.path.exists(os.path.abspath(work_dir))
  if exists and not args.directory:
    shutil.rmtree(work_dir)
    print("Deleting temporary dir:{0}".format(work_dir))

class Slack:
  def __init__(self, config, token_file):
    self.disabled = True
    try:
      from slackclient import SlackClient
    except:
      print("Warning: SlackClient library not found, not using slack\n", file=sys.stderr)
      return

    try:
      self.channel = config['channel']
      self.method = config['method']
      self.username = config['username']
      self.emoji = config['emoji']
    except (TypeError, KeyError) as e:
      print("Warning: slack not setup in config (error: %s). Not using slack.\n" % e, file=sys.stderr)
      return

    try:
      with open(token_file) as stoken:
        r = stoken.readlines()
      slack_token = ''.join(r).strip()
      self.client = SlackClient(slack_token)
    except IOError:
      print("Warning: slack token file %s not found/readable. Not using slack.\n" % token_file, file=sys.stderr)
      return

    self.disabled = False

  def api_call(self, text):
    if not self.disabled:
      self.client.api_call(self.method, channel=self.channel, username=self.username, icon_emoji=self.emoji, text=text)


# Author: cwhitten
# Purpose: Initial plumbing for a standardized deployment
#          process into the ClusterOS
#
# Keys off of a master config file in APP_ROOT/config/
#   with the naming convention APP_NAME.json
# Container-specific Marathon files live in APP_ROOT/templates/ with the
#   naming convention APP_NAME-SERVICE_NAME.json
#
# See README for details and intended use.
#
# Attempts to get a version from an existing image on marathon (formatting rules apply)

# Expected format:
#   <host>:<port>/moz-content-agora-7da406eb9e8937875e0548ae1149/v0.46
def getNextVersion(config, roger_env, application, branch, work_dir, repo, args, gitObj):
  sha = getGitSha(work_dir, repo, branch, gitObj)
  docker_search = subprocess.check_output("docker search {0}/{1}-{2}".format(roger_env['registry'], config['name'], application), shell=True)
  image_version_list = []
  version = ''
  envs = []
  for each_key in roger_env["environments"].keys():
      envs.append(each_key)
  for line in docker_search.split('\n'):
    image = line.split(' ')[0]
    matchObj = re.match("^{0}-{1}-.*/v.*".format(config['name'], application), image)
    if matchObj and matchObj.group().startswith(config['name'] + '-' + application):
      skip_image = False
      for env in envs:
        if matchObj.group().startswith("{0}-{1}-{2}".format(config['name'], application, env)):
          skip_image = True
          break
      if skip_image == False:
        image_version_list.append(matchObj.group().split('/v')[1])

  if len(image_version_list) == 0:	#Create initial version
    version = "{0}/v0.1.0".format(sha)
    print("No version currently exist in the Docker Registry. \nDeploying version:{0}".format(version))
  else:
    version = incrementVersion(sha, image_version_list, args)
  return version

def incrementVersion(sha, image_version_list, args):
  latest = max(image_version_list, key=splitVersion)
  ver_tuple = splitVersion(latest)
  latest_version = ''
  if args.incr_major:
    latest_version = "{0}/v{1}.0.0".format(sha, (int(ver_tuple[0])+1))
    return latest_version
  if args.incr_patch:
    latest_version = "{0}/v{1}.{2}.{3}".format(sha, int(ver_tuple[0]), int(ver_tuple[1]), (int(ver_tuple[2])+1))
    return latest_version

  latest_version = "{0}/v{1}.{2}.0".format(sha, int(ver_tuple[0]), (int(ver_tuple[1])+1))
  return latest_version

def splitVersion(version):
  major, _, rest = version.partition('.')
  minor, _, rest = rest.partition('.')
  patch, _, rest = rest.partition('.')
  return int(major), int(minor) if minor else 0, int(patch) if patch else 0

def getGitSha(work_dir, repo, branch, gitObj):
  return  gitObj.getGitSha(repo, branch, work_dir)

def describe():
  return 'runs through all of the steps: gitpull -> build & push to registry -> push to roger mesos.'

def parseArgs():
  parser = argparse.ArgumentParser(prog='roger deploy', description=describe())
  parser.add_argument('-e', '--environment', metavar='env',
    help="environment to deploy to. Example: 'dev' or 'stage'")
  parser.add_argument('application', metavar='application',
    help="application to deploy. Example: 'all' or 'kairos'")
  parser.add_argument('-b', '--branch', metavar='branch',
    help="branch to pull code from. Defaults to master. Example: 'production' or 'master'")
  parser.add_argument('-s', '--skip-build', action="store_true",
    help="whether to skip the build step. Defaults to false.'")
  parser.add_argument('config_file', metavar='config_file',
    help="configuration file to be use. Example: 'content.json' or 'kwe.json'")
  parser.add_argument('-M', '--incr-major', action="store_true",
    help="increment major in version. Defaults to false.'")
  parser.add_argument('-sp', '--skip-push', action="store_true",
    help="skip the push step. Defaults to false.'")
  parser.add_argument('-p', '--incr-patch', action="store_true",
    help="increment patch in version. Defaults to false.'")
  parser.add_argument('-S', '--secrets-file',
    help="specifies an optional secrets file for deployment runtime variables.")
  parser.add_argument('-d', '--directory',
    help="working directory. Uses a temporary directory if not specified.")
  return parser

def push(root, app, work_dir, image_name, config_file, environment, secrets_file, args):
  if secrets_file:
    secrets = "-S " + secrets_file
  else:
    secrets = ""
  try:
    push_command = (root, app, os.path.abspath(work_dir), image_name, config_file, environment, secrets)
    if args.skip_push == True:
      exit_code = os.system("{0}/cli/roger_push.py --skip-push {1} {2} \"{3}\" {4} --env {5} {6}".format(*push_command))
    else:
      exit_code = os.system("{0}/cli/roger_push.py {1} {2} \"{3}\" {4} --env {5} {6}".format(*push_command))
    return exit_code
  except (IOError) as e:
    print("The folowing error occurred.(Error: %s).\n" % e, file=sys.stderr)
    removeDirTree(work_dir, args)
    sys.exit('Exiting')

def pullRepo(root, app, work_dir, config_file, branch, args, settingObj, appObj, gitObj):

  args.app_name = app
  args.directory = work_dir

  try:
    exit_code = roger_gitpull.main(settingObj, appObj, gitObj, args)
    return exit_code
  except (IOError) as e:
    print("The folowing error occurred.(Error: %s).\n" % e, file=sys.stderr)
    removeDirTree(work_dir, args)
    sys.exit('Exiting')

def main(settingObject, appObject, frameworkUtilsObject, gitObj, args):
  settingObj = settingObject
  appObj = appObject
  config_dir = settingObj.getConfigDir()
  root = settingObj.getCliDir()
  roger_env = appObj.getRogerEnv(config_dir)
  config = appObj.getConfig(config_dir, args.config_file)
  if args.application not in config['apps']:
    print('Application specified not found.')
    # Return exit code to caller
    return 1

  if 'registry' not in roger_env:
    print('Registry not found in roger-env.json file.')
    # Returning exit code for caller to catch
    return 1

  #Setup for Slack-Client, token, and git user
  slack = Slack(config['notifications'], '/home/vagrant/.roger_cli.conf.d/slack_token')

  if args.application == 'all':
    apps = config['apps'].keys()
  else:
    apps = [args.application]

  common_repo = config.get('repo', '')
  environment = roger_env.get('default', '')

  work_dir = ''
  if args.directory:
    work_dir = args.directory
    print("Using {0} as the working directory".format(work_dir))
  else:
    work_dir = mkdtemp()
    print("Created a temporary dir: {0}".format(work_dir))

  if args.environment is None:
    if "ROGER_ENV" in os.environ:
      env_var = os.environ.get('ROGER_ENV')
      if env_var.strip() == '':
        print("Environment variable $ROGER_ENV is not set. Using the default set from roger-env.json file")
      else:
        print("Using value {} from environment variable $ROGER_ENV".format(env_var))
        environment = env_var
  else:
    environment = args.environment

  if environment not in roger_env['environments']:
    removeDirTree(work_dir, args)
    print('Environment not found in roger-env.json file.')
    # Returning exit code for caller to catch
    return 1

  branch = "master"     #master by default
  if not args.branch is None:
    branch = args.branch

  for app in apps:
    deployApp(settingObject, appObject, frameworkUtilsObject, gitObj, root, args, config, roger_env, work_dir, config_dir, environment, app, branch, slack, args.config_file, common_repo)

def deployApp(settingObject, appObject, frameworkUtilsObject, gitObj, root, args, config, roger_env, work_dir, config_dir, environment, app, branch, slack, config_file, common_repo):
  startTime = datetime.now()
  settingObj = settingObject
  appObj = appObject
  frameworkUtils = frameworkUtilsObject
  environmentObj = roger_env['environments'][environment]
  data = appObj.getAppData(config_dir, config_file, app)
  frameworkObj = frameworkUtils.getFramework(data)
  framework = frameworkObj.getName()

  repo = ''
  if common_repo != '':
    repo = data.get('repo', common_repo)
  else:
    repo = data.get('repo', args.application)

  image_name = ''
  image = ''

  # get/update target source(s)
  try:
    exit_code = pullRepo(root, app, os.path.abspath(work_dir), config_file, branch, args, settingObj, appObj, gitObj)
    if exit_code != 0:
      removeDirTree(work_dir, args)
      sys.exit('Exiting')
  except (IOError) as e:
    print("The folowing error occurred.(Error: %s).\n" % e, file=sys.stderr)
    removeDirTree(work_dir, args)
    sys.exit('Exiting')

  skip_build = False
  if args.skip_build is not None:
    skip_build = args.skip_build

  skip_push = False
  if args.skip_push is not None:
    skip_push = args.skip_push

  secrets_file = None
  if args.secrets_file is not None:
    secrets_file = args.secrets_file

  #Set initial version
  image_git_sha = getGitSha(work_dir, repo, branch, gitObj)
  image_name = "{0}-{1}-{2}/v0.1.0".format(config['name'], app, image_git_sha)

  if skip_build == True:
    curr_image_ver = frameworkObj.getCurrentImageVersion(roger_env, environment, app)
    print("Current image version deployed on {0} is :{1}".format(framework, curr_image_ver))
    if not curr_image_ver is None:
      image_name = "{0}-{1}-{2}".format(config['name'], app, curr_image_ver)
      print("Image current version from {0} endpoint is:{1}".format(framework, image_name))
    else:
      print("Using base version for image:{0}".format(image_name))
  else:
    #Docker build,tag and push
    image_name = getNextVersion(config, roger_env, app, branch, work_dir, repo, args, gitObj)
    image_name = "{0}-{1}-{2}".format(config['name'], app, image_name)
    print("Bumped up image to version:{0}".format(image_name))
    try:
      exit_code = os.system("{0}/cli/roger_build.py --push {1} {2} {3} {4}".format(root, app, os.path.abspath(work_dir), image_name, config_file))
      if exit_code != 0:
        removeDirTree(work_dir, args)
        sys.exit('Exiting')
    except (IOError) as e:
      print("The folowing error occurred.(Error: %s).\n" % e, file=sys.stderr)
      removeDirTree(work_dir, args)
      sys.exit('Exiting')
  print("Version is:"+image_name)

  #Deploying the app to framework
  try:
    exit_code = push(root, app, os.path.abspath(work_dir), image_name, config_file, environment, secrets_file, args)
    if exit_code != 0:
      removeDirTree(work_dir, args)
      sys.exit('Exiting')
  except (IOError) as e:
    print("The folowing error occurred.(Error: %s).\n" % e, file=sys.stderr)
    removeDirTree(work_dir, args)
    sys.exit('Exiting')

  removeDirTree(work_dir, args)

  deployTime = datetime.now() - startTime

  try:
      git_username = subprocess.check_output("git config user.name", shell=True)
  except subprocess.CalledProcessError as e:
      print("git config user.name not found. Setting default git_username as unknown")
      git_username = "unknown"

  deployMessage = "{0}'s deploy for {1} / {2} / {3} completed in {4} seconds.".format(
    git_username.rstrip(), app, environment, branch, deployTime.total_seconds())
  slack.api_call(deployMessage)
  print(deployMessage)


if __name__ == "__main__":
  settingObj = Settings()
  appObj = AppConfig()
  frameworkUtils = FrameworkUtils()
  gitObj = GitUtils()
  parser = parseArgs()
  args = parser.parse_args()
  main(settingObj, appObj, frameworkUtils, gitObj, args)
