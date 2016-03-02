#!/usr/bin/python

from __future__ import print_function
import unittest
import os
import argparse
import json
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, "cli")))
import roger_push
from marathon import Marathon
from frameworkutils import FrameworkUtils
from appconfig import AppConfig
from settings import Settings
from mockito import mock, when, verify
from mock import MagicMock
from settings import Settings

#Test basic functionalities of roger-push script
class TestPush(unittest.TestCase):

  def setUp(self):
    parser = argparse.ArgumentParser(description='Args for test')
    parser.add_argument('-e', '--env', metavar='env', help="Environment to deploy to. example: 'dev' or 'stage'")
    parser.add_argument('--skip-push', '-s', help="Don't push. Only generate components. Defaults to false.", action="store_true")
    parser.add_argument('--secrets-file', '-S', help="Specify an optional secrets file for deploy runtime variables.")
    self.parser = parser
    self.args = parser

    self.settingObj = Settings()
    self.base_dir = self.settingObj.getCliDir()
    self.configs_dir = self.base_dir+"/tests/configs"
    self.components_dir = self.base_dir+'/tests/components/dev'

    with open(self.configs_dir+'/app.json') as config:
      config = json.load(config)
    with open(self.configs_dir+'/roger-env.json') as roger:
      roger_env = json.load(roger)
    data = config['apps']['grafana_test_app']
    self.config = config
    self.roger_env = roger_env
    self.data = data
    with open(self.configs_dir+'/app.json') as test_config:
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
    when(marathon).put(self.components_dir+'/test-roger-grafana.json', roger_env['environments']['dev'], 'grafana_test_app').thenReturn("Response [200]")
    frameworkUtils = mock(FrameworkUtils)
    when(frameworkUtils).getFramework(data).thenReturn(marathon)
    when(settings).getComponentsDir().thenReturn(self.base_dir+"/tests/components")
    when(settings).getSecretsDir().thenReturn(self.base_dir+"/tests/secrets")
    when(settings).getTemplatesDir().thenReturn(self.base_dir+"/tests/templates")
    when(settings).getConfigDir().thenReturn(self.configs_dir)
    when(settings).getCliDir().thenReturn(self.base_dir)
    when(appConfig).getRogerEnv(self.configs_dir).thenReturn(roger_env)
    when(appConfig).getConfig(self.configs_dir, "app.json").thenReturn(config)
    when(appConfig).getAppData(self.configs_dir, "app.json", "grafana_test_app").thenReturn(data)

    args = self.args
    args.env = "dev"
    args.secrets_file=""
    args.skip_push=True
    args.app_name = 'grafana_test_app'
    args.config_file = 'app.json'
    args.directory = self.base_dir+'/tests/testrepo'
    args.image_name = 'grafana/grafana:2.1.3'
    object_list = []
    object_list.append(settings)
    object_list.append(appConfig)
    object_list.append(frameworkUtils)
    roger_push.main(object_list, args)
    with open(self.components_dir+'/test-app-grafana.json') as output:
      output = json.load(output)
    assert output['container']['docker']['image'] == "grafana/grafana:2.1.3"
    verify(settings).getConfigDir()
    verify(settings).getComponentsDir()
    verify(settings).getTemplatesDir()
    verify(settings).getSecretsDir()
    verify(frameworkUtils).getFramework(data)

  def test_container_resolution(self):
    settings = mock(Settings)
    appConfig = mock(AppConfig)
    marathon = mock(Marathon)
    roger_env = self.roger_env
    config = self.test_config
    data = self.test_data
    when(marathon).put(self.components_dir+'/test-app-grafana.json', roger_env['environments']['dev'], 'grafana').thenReturn("Response [200]")
    when(marathon).put(self.components_dir+'/test-app-grafana1.json', roger_env['environments']['dev'], 'grafana1').thenReturn("Response [200]")
    when(marathon).put(self.components_dir+'/test-app-grafana2.json', roger_env['environments']['dev'], 'grafana2').thenReturn("Response [200]")
    frameworkUtils = mock(FrameworkUtils)
    when(frameworkUtils).getFramework(data).thenReturn(marathon)
    when(settings).getComponentsDir().thenReturn(self.base_dir+"/tests/components")
    when(settings).getSecretsDir().thenReturn(self.base_dir+"/tests/secrets")
    when(settings).getTemplatesDir().thenReturn(self.base_dir+"/tests/templates")
    when(settings).getConfigDir().thenReturn(self.configs_dir)
    when(settings).getCliDir().thenReturn(self.base_dir)
    when(appConfig).getRogerEnv(self.configs_dir).thenReturn(roger_env)
    when(appConfig).getConfig(self.configs_dir, "app.json").thenReturn(config)
    when(appConfig).getAppData(self.configs_dir, "app.json", "grafana_test_app").thenReturn(data)

    args = self.args
    args.env="dev"
    args.secrets_file=""
    args.skip_push=True
    args.app_name = 'grafana_test_app'
    args.config_file = 'app.json'
    args.directory = self.base_dir+'/tests/testrepo'
    args.image_name = 'grafana/grafana:2.1.3'
    object_list = []
    object_list.append(settings)
    object_list.append(appConfig)
    object_list.append(frameworkUtils)
    roger_push.main(object_list, args)
    with open(self.components_dir+'/test-app-grafana.json') as output:
      output = json.load(output)
    assert output['container']['docker']['image'] == "grafana/grafana:2.1.3"
    assert output['cpus'] == 2
    assert output['mem'] == 1024
    assert output['uris'] == [ "abc", "xyz", "$ENV_VAR" ]
    with open(self.components_dir+'/test-app-grafana1.json') as output:
      output = json.load(output)
    assert output['container']['docker']['image'] == "grafana/grafana:2.1.3"
    assert output['cpus'] == 0.5
    assert output['mem'] == 512
    with open(self.components_dir+'/test-app-grafana2.json') as output:
      output = json.load(output)
    assert output['container']['docker']['image'] == "grafana/grafana:2.1.3"
    assert output['cpus'] == 1
    assert output['mem'] == 1024

  def tearDown(self):
    pass

if __name__ == '__main__':
  unittest.main()
