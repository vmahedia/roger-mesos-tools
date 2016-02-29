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
from containerconfig import ContainerConfig

def parse_args():
  parser = argparse.ArgumentParser(description='Get an Interactive Bash session into your container.')
  parser.add_argument('appTaskId', metavar='appTaskId', help="Application Task Id to uniquely \
    identify a container Id. example: 'content.56847afe9799")
  parser.add_argument('-e', '--env', metavar='env', help="Environment to search. \
    example: 'dev' or 'stage'")
  parser.add_argument('-H','--hostname', metavar='hostname', help="Hostname to search.\
    example: 'daldevmesos01' or 'daldevmesos04'")
  return parser

def main():
  parser = parse_args()
  args = parser.parse_args()
  config_dir = settingObj.getConfigDir()
  roger_env = appObj.getRogerEnv(config_dir)
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

  hostname = ''
  containerId = ''
  if args.hostname == None:
    hostname = containerconfig.get_hostname_from_marathon(environment, roger_env, args.appTaskId);
  else:
    hostname = args.hostname;

  if hostname != '':	#Hostname maybe empty when the given appTaskId does not match any taskId from Marathon
    containerId = containerconfig.get_containerid(args.appTaskId, hostname);
  else:
    print("Most likely hostname could not be retrieved with appTaskId {0}. Hostname is also \
an optional argument. See -h for usage.".format(args.appTaskId));

  if containerId != '' and containerId != None:
    print("If there are multiple containers that pattern match the given mesos task Id, \
then will log into the first one")
    print("Executing bash in docker container - {0} on host - {1} for application task id - {2}".format(containerId, hostname, args.appTaskId));
    try:
      subprocess.check_call("docker -H tcp://{0}:4243 exec -it {1} bash".format(hostname, containerId), shell=True);
    except Exception as e:
      print("The following error occurred:\n (error: %s).\n" % e, file=sys.stderr)
  else:
    print("No Container found on host {0} with application Task Id {1}".format(hostname, args.appTaskId));

if __name__ == '__main__':
  settingObj = Settings()
  appObj = AppConfig()
  containerconfig = ContainerConfig()
  main()
