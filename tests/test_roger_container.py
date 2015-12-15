#!/usr/bin/python

from __future__ import print_function
import unittest
import os
import argparse
import json
import sys
sys.path.append('/vagrant/cli')
import imp
roger_push = imp.load_source('roger_push', '/vagrant/cli/roger-push')
from marathon import Marathon
from frameworkutils import FrameworkUtils
from appconfig import AppConfig
from settings import Settings
from mockito import mock, when, verify
from mock import MagicMock

#Test basic functionalities of roger-push script
class TestPush(unittest.TestCase):

  def setUp(self):
    parser = argparse.ArgumentParser(description='Args for test')
    parser.add_argument('-e', '--env', metavar='env', help="Environment to deploy to. example: 'dev' or 'stage'")
    parser.add_argument('--skip-push', '-s', help="Don't push. Only generate components. Defaults to false.", action="store_true")
    self.parser = parser
    with open('/vagrant/config/roger_tests.json') as config:
      config = json.load(config)
    with open('/vagrant/config/roger-env.json') as roger:
      roger_env = json.load(roger)
    data = config['apps']['container-vars']
    self.config = config
    self.roger_env = roger_env
    self.data = data

  def test_rogerPush(self):
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
    when(settings).getTemplatesDir().thenReturn("/vagrant/templates")
    when(settings).getConfigDir().thenReturn("/vagrant/config")
    when(settings).getCliDir().thenReturn("/vagrant")
    when(appConfig).getRogerEnv("/vagrant/config").thenReturn(roger_env)
    when(appConfig).getConfig("/vagrant/config", "roger_tests.json").thenReturn(config)
    when(appConfig).getAppData("/vagrant/config", "roger_tests.json", "container-vars").thenReturn(data)
    parser = self.parser
    args = parser.parse_args()
    args.app_name = 'container-vars'
    args.config_file = 'roger_tests.json'
    args.directory = '/vagrant/tests/testrepo'
    args.image_name = 'tests/v0.1.0'
    object_list = []
    object_list.append(settings)
    object_list.append(appConfig)
    object_list.append(frameworkUtils)

    roger_push.main(object_list, args)

    with open('/vagrant/tests/components/dev/roger-tests-tests.json') as output:
      output = json.load(output)


    dict_output = eval(output["env"]["ENV_VAR_CONTAINER"])

    print ("Test Case 1: Executing Test to Match Environment Variable and Gloabl Variable Within a Container")
    print()
    print ("Expected Value -> Production Environment : production")
    print ("Actual Value   : {}".format(str(dict_output['prod']['NODE_ENV'])))

    print()
    print ("Expected Value -> Development Environment : development")
    print ("Actual Value   : {}".format(str(dict_output['dev']['NODE_ENV'])))

    print()
    print ("Expected Value -> Staging Environment : staging")
    print ("Actual Value   : {}".format(str(dict_output['stage']['NODE_ENV'])))

    print ("Expected Value -> GLOBAL_VAR_CONTAINER : ")
    print ("Actual Value   : {}".format(str(output["env"]["GLOBAL_VAR_CONTAINER"])))

    assert str(dict_output['prod']['NODE_ENV']) == "production"
    assert str(dict_output['stage']['NODE_ENV']) == "staging"
    assert str(dict_output['dev']['NODE_ENV']) == "development"
    assert str(output["env"]["GLOBAL_VAR_CONTAINER"]) == ""



  def tearDown(self):
    pass

if __name__ == '__main__':
  unittest.main()
