#!/usr/bin/env python

from __future__ import print_function
import argparse
import subprocess
import json
import os
import requests
import subprocess
import sys
from marathon import Marathon
from cli.utils import printException, printErrorMsg
requests.packages.urllib3.disable_warnings()

# we probably need to remove (or refactor) this module (ankan, 201603)


class ContainerConfig:

    def get_hostname_from_marathon(self, environment, roger_env, appTaskId):
        hostname = ''
        marathon = Marathon()
        tasks = marathon.getTasks(roger_env, environment)
        for task in tasks:
            if task['id'].startswith(appTaskId):
                hostname = task['host']

        return hostname

    def get_containerid_mesostaskid(self, appTaskId, hostname):
        containerId = ''
        mesosTaskId = ''
        try:
            containers = subprocess.check_output(
                "docker -H tcp://{}:4243 ps -q".format(hostname), shell=True)
        except:
            print("No route to host. Please check hostname '{}'".format(
                hostname), file=sys.stderr)
            return
        for container in containers.split('\n'):
            if container.strip() != '':
                try:
                    mesosTaskId = subprocess.check_output("docker -H tcp://{0}:4243 exec {1} \
          printenv MESOS_TASK_ID".format(hostname, container), stderr=subprocess.STDOUT, shell=True)
                except Exception as e:
                    if ("Cannot connect to the Docker daemon" in str(e.output)):
                        printException(e)
                        break
                    else:
                        # This is the case when a container does not have a
                        # MESOS_TASK_ID in its ENV variables
                        pass
                if mesosTaskId.startswith(appTaskId):
                    containerId = container.strip()
                    break
        return containerId, mesosTaskId
