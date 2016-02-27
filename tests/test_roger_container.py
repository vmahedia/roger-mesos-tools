#!/usr/bin/python

from __future__ import print_function
import unittest
import os
import argparse
import json
import sys
sys.path.append('/vagrant/cli')
import imp
roger_push = imp.load_source('roger_push', '/vagrant/cli/roger-push.py')
from marathon import Marathon
from frameworkutils import FrameworkUtils
from appconfig import AppConfig
from settings import Settings
from mockito import mock, when, verify
from mock import MagicMock

#Test basic functionalities of roger-push script
class Testcontainer(unittest.TestCase):

  def setUp(self):
    parser = argparse.ArgumentParser(description='Args for test')
    parser.add_argument('-e', '--env', metavar='env', help="Environment to deploy to. example: 'dev' or 'stage'")
    parser.add_argument('--skip-push', '-s', help="Don't push. Only generate components. Defaults to false.", action="store_true")
    parser.add_argument('--secrets-file', '-S',
      help="Specify an optional secrets file for deploy runtime variables.")
    self.parser = parser
    with open('/vagrant/tests/configs/roger_single_container_var_tests.json') as config:
      config = json.load(config)
    with open('/vagrant/tests/configs/roger-env.json') as roger:
      roger_env = json.load(roger)
    data = config['apps']['container-vars']
    self.config = config
    self.roger_env = roger_env
    self.data = data

  def test_vars_single_container(self):
    settings = mock(Settings)
    appConfig = mock(AppConfig)
    marathon = mock(Marathon)
    roger_env = self.roger_env
    config = self.config
    data = self.data
    frameworkUtils = mock(FrameworkUtils)
    when(frameworkUtils).getFramework(data).thenReturn(marathon)
    when(settings).getComponentsDir().thenReturn("/vagrant/tests/components")
    when(settings).getSecretsDir().thenReturn("/vagrant/tests/secrets")
    when(settings).getTemplatesDir().thenReturn("/vagrant/tests/templates")
    when(settings).getConfigDir().thenReturn("/vagrant/tests/configs")
    when(settings).getCliDir().thenReturn("/vagrant")
    when(appConfig).getRogerEnv("/vagrant/tests/configs").thenReturn(roger_env)
    when(appConfig).getConfig("/vagrant/tests/configs", "roger_single_container_var_tests.json").thenReturn(config)

    when(appConfig).getAppData("/vagrant/tests/configs", "roger_single_container_var_tests.json", "container-vars").thenReturn(data)
    parser = self.parser
    args = parser.parse_args()
    args.app_name = 'container-vars'
    args.config_file = 'roger_single_container_var_tests.json'
    args.directory = '/vagrant/tests/testrepo'
    args.image_name = 'tests/v0.1.0'
    object_list = []
    object_list.append(settings)
    object_list.append(appConfig)
    object_list.append(frameworkUtils)

    roger_push.main(object_list, args)

    with open('/vagrant/tests/components/dev/roger-single-container-var-tests.json') as output:
      output = json.load(output)

    var1 = output["env"]["VAR_1"]
    var3 = output["env"]["VAR_3"]
    var4 = output["env"]["VAR_4"]

    print ("Expected Value -> Var1 : environment_value_1")
    print ("Actual Value   : {}".format(var1))

    print ("Expected Value -> Var3 : value_3")
    print ("Actual Value   : {}".format(var3))

    assert var3 == "value_3"
    assert var1 == "environment_value_1"

  def tearDown(self):
    pass

if __name__ == '__main__':
  unittest.main()
