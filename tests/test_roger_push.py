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
    parser.add_argument('--secrets-file', '-S', help="Specify an optional secrets file for deploy runtime variables.")
    self.parser = parser
    with open('/vagrant/config/roger.json') as config:
      config = json.load(config)
    with open('/vagrant/config/roger-env.json') as roger:
      roger_env = json.load(roger)
    data = config['apps']['grafana']
    self.config = config
    self.roger_env = roger_env
    self.data = data
    with open('/vagrant/tests/configs/app.json') as test_config:
      test_config = json.load(test_config)
    test_data = test_config['apps']['grafana_test_app']
    self.test_config = test_config
    self.test_data = test_data

  def test_rogerPush(self):
    settings = mock(Settings)
    appConfig = mock(AppConfig)
    marathon = mock(Marathon)
    roger_env = self.roger_env
    config = self.config
    data = self.data
    when(marathon).put('/vagrant/tests/components/dev/moz-roger-grafana.json', roger_env['environments']['dev'], 'grafana').thenReturn("Response [200]")
    frameworkUtils = mock(FrameworkUtils)
    when(frameworkUtils).getFramework(data).thenReturn(marathon)
    when(settings).getComponentsDir().thenReturn("/vagrant/tests/components")
    when(settings).getSecretsDir().thenReturn("/vagrant/tests/secrets")
    when(settings).getTemplatesDir().thenReturn("/vagrant/templates")
    when(settings).getConfigDir().thenReturn("/vagrant/config")
    when(settings).getCliDir().thenReturn("/vagrant")
    when(appConfig).getRogerEnv("/vagrant/config").thenReturn(roger_env)
    when(appConfig).getConfig("/vagrant/config", "roger.json").thenReturn(config)
    when(appConfig).getAppData("/vagrant/config", "roger.json", "grafana").thenReturn(data)
    parser = self.parser
    args = parser.parse_args()
    args.app_name = 'grafana'
    args.config_file = 'roger.json'
    args.directory = '/vagrant/tests/testrepo'
    args.image_name = 'grafana/grafana:2.1.3'
    object_list = []
    object_list.append(settings)
    object_list.append(appConfig)
    object_list.append(frameworkUtils)
    roger_push.main(object_list, args)
    with open('/vagrant/tests/components/dev/moz-roger-grafana.json') as output:
      output = json.load(output)
    assert output['container']['docker']['image'] == "registry.roger.dal.moz.com:5000/grafana/grafana:2.1.3"
    verify(settings).getConfigDir()
    verify(settings).getComponentsDir()
    verify(settings).getTemplatesDir()
    verify(settings).getSecretsDir()
    verify(frameworkUtils).getFramework(data)
    verify(marathon).put('/vagrant/tests/components/dev/moz-roger-grafana.json', roger_env['environments']['dev'], 'grafana')

  def test_container_resolution(self):
    settings = mock(Settings)
    appConfig = mock(AppConfig)
    marathon = mock(Marathon)
    roger_env = self.roger_env
    config = self.test_config
    data = self.test_data
    when(marathon).put('/vagrant/tests/components/dev/test-app-grafana.json', roger_env['environments']['dev'], 'grafana').thenReturn("Response [200]")
    when(marathon).put('/vagrant/tests/components/dev/test-app-grafana1.json', roger_env['environments']['dev'], 'grafana1').thenReturn("Response [200]")
    when(marathon).put('/vagrant/tests/components/dev/test-app-grafana2.json', roger_env['environments']['dev'], 'grafana2').thenReturn("Response [200]")
    frameworkUtils = mock(FrameworkUtils)
    when(frameworkUtils).getFramework(data).thenReturn(marathon)
    when(settings).getComponentsDir().thenReturn("/vagrant/tests/components")
    when(settings).getSecretsDir().thenReturn("/vagrant/tests/secrets")
    when(settings).getTemplatesDir().thenReturn("/vagrant/tests/templates")
    when(settings).getConfigDir().thenReturn("/vagrant/tests/configs")
    when(settings).getCliDir().thenReturn("/vagrant")
    when(appConfig).getRogerEnv("/vagrant/tests/configs").thenReturn(roger_env)
    when(appConfig).getConfig("/vagrant/tests/configs", "app.json").thenReturn(config)
    when(appConfig).getAppData("/vagrant/tests/configs", "app.json", "grafana_test_app").thenReturn(data)
    parser = self.parser
    args = parser.parse_args()
    args.app_name = 'grafana_test_app'
    args.config_file = 'app.json'
    args.directory = '/vagrant/tests/testrepo'
    args.image_name = 'grafana/grafana:2.1.3'
    object_list = []
    object_list.append(settings)
    object_list.append(appConfig)
    object_list.append(frameworkUtils)
    roger_push.main(object_list, args)
    with open('/vagrant/tests/components/dev/test-app-grafana.json') as output:
      output = json.load(output)
    assert output['container']['docker']['image'] == "grafana/grafana:2.1.3"
    assert output['cpus'] == 2
    assert output['mem'] == 1024
    assert output['uris'] == [ "abc", "xyz", "$ENV_VAR" ]
    with open('/vagrant/tests/components/dev/test-app-grafana1.json') as output:
      output = json.load(output)
    assert output['container']['docker']['image'] == "grafana/grafana:2.1.3"
    assert output['cpus'] == 0.5
    assert output['mem'] == 512
    with open('/vagrant/tests/components/dev/test-app-grafana2.json') as output:
      output = json.load(output)
    assert output['container']['docker']['image'] == "grafana/grafana:2.1.3"
    assert output['cpus'] == 1
    assert output['mem'] == 1024

  def tearDown(self):
    pass

if __name__ == '__main__':
  unittest.main()
