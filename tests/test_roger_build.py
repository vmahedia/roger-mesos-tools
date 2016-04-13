#!/usr/bin/python

from __future__ import print_function
import unittest
import argparse
import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, "cli")))
from roger_build import RogerBuild
from appconfig import AppConfig
from settings import Settings
from mockito import mock, when, verify
from mockito.matchers import any
from hooks import Hooks

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

  def test_roger_build_with_no_app_fails(self):
    settings = mock(Settings)
    appConfig = mock(AppConfig)
    roger_build = RogerBuild()
    mockedHooks = mock(Hooks)
    roger_env = self.roger_env
    config = self.config
    data = self.data
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

    return_code = roger_build.main(settings, appConfig, mockedHooks, args)
    assert return_code == 1

  def test_roger_build_calls_prebuild_hook_when_present(self):
    settings = mock(Settings)
    appConfig = mock(AppConfig)
    roger_build = RogerBuild()
    mockedHooks = mock(Hooks)
    roger_env = {}
    roger_env["registry"] = "any registry"
    when(appConfig).getRogerEnv(any()).thenReturn(roger_env)
    appdata = {}
    appdata["hooks"]=dict([("pre_build", "some command")])
    when(appConfig).getAppData(any(), any(), any()).thenReturn(appdata)
    config = self.config
    when(appConfig).getConfig(any(), any()).thenReturn(config)
    args = self.args
    args.config_file = 'any.json'
    args.app_name = 'any app'
    args.directory = '/tmp'
    when(mockedHooks).run_hook(any(), any(), any()).thenReturn(0)
    return_code = roger_build.main(settings, appConfig, mockedHooks, args)
    verify(mockedHooks).run_hook("pre_build", any(), any())

  def test_roger_build_calls_postbuild_hook_when_present(self):
    settings = mock(Settings)
    appConfig = mock(AppConfig)
    roger_build = RogerBuild()
    mockedHooks = mock(Hooks)
    roger_env = {}
    roger_env["registry"] = "any registry"
    when(appConfig).getRogerEnv(any()).thenReturn(roger_env)
    appdata = {}
    appdata["hooks"]=dict([("post_build", "some command")])
    when(appConfig).getAppData(any(), any(), any()).thenReturn(appdata)
    config = self.config
    when(appConfig).getConfig(any(), any()).thenReturn(config)
    args = self.args
    args.config_file = 'any.json'
    args.app_name = 'any app'
    args.directory = '/tmp'
    when(mockedHooks).run_hook(any(), any(), any()).thenReturn(0)
    return_code = roger_build.main(settings, appConfig, mockedHooks, args)
    verify(mockedHooks).run_hook("post_build", any(), any())

  def tearDown(self):
    pass

if __name__ == '__main__':
  unittest.main()
