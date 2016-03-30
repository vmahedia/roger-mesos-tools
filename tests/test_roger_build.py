#!/usr/bin/python

from __future__ import print_function
import unittest
import argparse
import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, "cli")))
import roger_build
from marathon import Marathon
from appconfig import AppConfig
from settings import Settings
from mockito import mock, when, verify
from mock import MagicMock

#Test basic functionalities of roger-build script
class TestBuild(unittest.TestCase):

  def setUp(self):
    parser = argparse.ArgumentParser(description='Args for test')
    parser.add_argument('app_name', metavar='app_name',
      help="application to build. Example: 'agora'.")
    parser.add_argument('directory', metavar='directory',
      help="working directory. Example: '/home/vagrant/work_dir'.")
    parser.add_argument('tag_name', metavar='tag_name',
      help="tag for the built image. Example: 'roger-collectd:0.20'.")
    parser.add_argument('config_file', metavar='config_file',
      help="configuration file to use. Example: 'content.json'.")
    parser.add_argument('--push', '-p', help="Also push to registry. Defaults to false.", action="store_true")

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

  def test_rogerBuild_noApp(self):
    settings = mock(Settings)
    appConfig = mock(AppConfig)
    marathon = mock(Marathon)
    roger_env = self.roger_env
    config = self.config
    data = self.data
    when(marathon).put(self.components_dir+'/test-roger-grafana.json', roger_env['environments']['dev'], 'grafana_test_app').thenReturn("Response [200]")
    when(settings).getComponentsDir().thenReturn(self.base_dir+"/tests/components")
    when(settings).getSecretsDir().thenReturn(self.base_dir+"/tests/secrets")
    when(settings).getTemplatesDir().thenReturn(self.base_dir+"/tests/templates")
    when(settings).getConfigDir().thenReturn(self.configs_dir)
    when(settings).getCliDir().thenReturn(self.base_dir)
    when(appConfig).getRogerEnv(self.configs_dir).thenReturn(roger_env)
    when(appConfig).getConfig(self.configs_dir, "app.json").thenReturn(config)
    when(appConfig).getAppData(self.configs_dir, "app.json", "grafana_test_app").thenReturn(data)
    args = self.args
    # Setting app_name as empty
    args.app_name = ''
    args.config_file = 'app.json'

    return_code = roger_build.main(settings, appConfig, args)
    assert return_code == 1

  def test_rogerBuild_noRegistry(self):
    settings = mock(Settings)
    appConfig = mock(AppConfig)
    marathon = mock(Marathon)
    roger_env = self.roger_env
    config = self.config
    data = self.data
    when(marathon).put(self.components_dir+'/test-roger-grafana.json', roger_env['environments']['dev'], 'grafana_test_app').thenReturn("Response [200]")
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
    config_dir = settings.getConfigDir()
    roger_env = appConfig.getRogerEnv(config_dir)
    # Remove registry key from dictionary
    del roger_env['registry']

    return_code = roger_build.main(settings, appConfig, args)
    assert return_code == 1

  def tearDown(self):
    pass

if __name__ == '__main__':
  unittest.main()
