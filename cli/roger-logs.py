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
  parser = argparse.ArgumentParser(description="This command keeps streaming the new output \
    from the container\'s STDOUT and STDERR logs.")
  parser.add_argument('appTaskId', metavar='appTaskId', help="Application Task Id to uniquely \
    identify a container Id. example: 'content.56847afe9799")
  parser.add_argument('-e', '--env', metavar='env', help="Environment to search. \
    example: 'dev' or 'stage'")
  parser.add_argument('-H','--hostname', metavar='hostname', help="Hostname to search.\
    example: 'daldevmesos01' or 'daldevmesos04'")
  parser.add_argument('-f', '--follow', help="Follow log output. Defaults to false.", action="store_true")
  parser.add_argument('-t', '--timestamps', help="Show timestamps. Defaults to false.", action="store_true")
  parser.add_argument('-s', '--since', help="Show logs since timestamp.")
  parser.add_argument('-T', '--tail', help="Number of lines to show from the end of the logs.\
    If a negative number is given, it shows all.")
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
    ( containerId, mesosTaskId ) = containerconfig.get_containerid_mesostaskid(args.appTaskId, hostname);
  else:
    print("Most likely hostname could not be retrieved with appTaskId {0}. Hostname is also \
an optional argument. See -h for usage.".format(args.appTaskId));

  if containerId != '' and containerId != None:
    print("If there are multiple containers that pattern match the given mesos task Id, \
then will log into the first one")
    print("Displaying logs in docker container - {0} on host - {1} for mesosTask Id {2}".format(containerId, hostname, mesosTaskId));
    command = "docker -H tcp://{0}:4243 logs ".format(hostname)
    if args.follow:
      command = "{} -f=true".format(command)
    else:
      command = "{} -f=false".format(command)
    if args.since:
       command = "{} --since=\"{}\"".format(command, args.since)
    if args.timestamps:
       command = "{} -t".format(command, args.since)
    if args.tail:
       command = "{} --tail=\"{}\"".format(command, args.tail)

    command = "{} {}".format(command, containerId)
    try:
      subprocess.check_call("{}".format(command),  shell=True);
    except (KeyboardInterrupt, SystemExit):
      print("Exited.")
    except (subprocess.CalledProcessError) as e:
      print("The following error occurred:\n (error: %s).\n" % e, file=sys.stderr)
  else:
    print("No Container found on host {0} with application Task Id {1}".format(hostname, args.appTaskId));

if __name__ == '__main__':
  settingObj = Settings()
  appObj = AppConfig()
  containerconfig = ContainerConfig()
  main()
