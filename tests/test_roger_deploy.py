#!/usr/bin/python

from __future__ import print_function
import unittest
import argparse
import os
import sys
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, "cli")))
import roger_push
import roger_deploy
import roger_gitpull
from marathon import Marathon
from frameworkUtils import FrameworkUtils
from appconfig import AppConfig
from settings import Settings
from mockito import mock, when, verify
from mock import MagicMock
from settings import Settings
from gitutils  import GitUtils

#Test basic functionalities of roger-deploy script
class TestDeploy(unittest.TestCase):

  def setUp(self):
    parser = argparse.ArgumentParser(description='Args for test')
    parser.add_argument('-e', '--environment', metavar='env',
    help="Environment to deploy to. example: 'dev' or 'stage'")
    parser.add_argument('-s', '--skip-build', action="store_true", help="Flag that skips roger-build when set to true. Defaults to false.'")
    parser.add_argument('-M', '--incr-major', action="store_true", help="Increment major in version. Defaults to false.'")
    parser.add_argument('-p', '--incr-patch', action="store_true", help="Increment patch in version. Defaults to false.'")
    parser.add_argument('-sp', '--skip-push', action="store_true", help="Flag that skips roger push when set to true. Defaults to false.'")
    parser.add_argument('-S', '--secrets-file', help="Specify an optional secrets file for deployment runtime variables.")
    parser.add_argument('-d', '--directory', help="Specify an optional directory to pull out the repo. This is the working directory.")
    self.parser = parser
    self.args = parser

    self.settingObj = Settings()
    self.base_dir = self.settingObj.getCliDir()
    self.configs_dir = self.base_dir+"/tests/configs"

    with open(self.configs_dir+'/app.json') as config:
      config = json.load(config)
    with open(self.configs_dir+'/roger-env.json') as roger:
      roger_env = json.load(roger)
    data = config['apps']['grafana_test_app']
    self.config = config
    self.roger_env = roger_env
    self.data = data

  def test_splitVersion(self):
    assert roger_deploy.splitVersion("0.1.0") == (0,1,0)
    assert roger_deploy.splitVersion("2.0013") == (2,13,0)

  def test_incrementVersion(self):
    git_sha = "dwqjdqgwd7y12edq21"
    image_version_list = ['0.001','0.2.034','1.1.2','1.002.1']

    args = self.args
    args.directory=""
    args.secrets_file=""
    args.incr_patch = True
    args.incr_major = True

    assert roger_deploy.incrementVersion(git_sha, image_version_list, args) == 'dwqjdqgwd7y12edq21/v2.0.0'
    assert roger_deploy.incrementVersion(git_sha, image_version_list, args) == 'dwqjdqgwd7y12edq21/v2.0.0'
    assert roger_deploy.incrementVersion(git_sha, image_version_list, args) == 'dwqjdqgwd7y12edq21/v2.0.0'

  def test_tempDirCheck(self):
    work_dir = "./test_dir"

    args = self.args
    args.directory=""
    args.skip_push=True
    args.secrets_file=""
    roger_deploy.removeDirTree(work_dir, args)
    exists = os.path.exists(os.path.abspath(work_dir))
    assert exists == False
    os.makedirs(work_dir)
    exists = os.path.exists(os.path.abspath(work_dir))
    assert exists == True
    roger_deploy.removeDirTree(work_dir, args)
    exists = os.path.exists(os.path.abspath(work_dir))
    assert exists == False

  def test_roger_deploy_with_no_app_fails(self):
    settings = mock(Settings)
    appConfig = mock(AppConfig)
    marathon = mock(Marathon)
    gitObj = mock(GitUtils)
    roger_env = self.roger_env
    config = self.config
    data = self.data
    when(marathon).getCurrentImageVersion(roger_env, 'dev', 'grafana').thenReturn("testversion/v0.1.0")
    frameworkUtils = mock(FrameworkUtils)
    when(frameworkUtils).getFramework(data).thenReturn(marathon)
    when(settings).getConfigDir().thenReturn(self.configs_dir)
    when(settings).getCliDir().thenReturn(self.base_dir)
    when(appConfig).getRogerEnv(self.configs_dir).thenReturn(roger_env)
    when(appConfig).getConfig(self.configs_dir, "app.json").thenReturn(config)
    when(appConfig).getAppData(self.configs_dir, "app.json", "grafana_test_app").thenReturn(data)

    args = self.args
    args.directory=""
    args.secrets_file=""
    args.environment="dev"
    args.skip_push=True
    args.application = ''
    args.config_file = 'app.json'
    args.skip_build = True
    args.branch = None
    os.environ["ROGER_CONFIG_DIR"] = self.configs_dir

    #roger_env = appConfig.getRogerEnv(self.configs_dir)
    #del roger_env['registry']
    roger_deploy.push = MagicMock(return_value=0)
    return_code = roger_deploy.main(settings, appConfig, frameworkUtils, gitObj, args)
    assert return_code == 1

  def test_roger_deploy_with_no_registry_fails(self):
    settings = mock(Settings)
    appConfig = mock(AppConfig)
    marathon = mock(Marathon)
    gitObj = mock(GitUtils)
    roger_env = self.roger_env
    config = self.config
    data = self.data
    when(marathon).getCurrentImageVersion(roger_env, 'dev', 'grafana').thenReturn("testversion/v0.1.0")
    frameworkUtils = mock(FrameworkUtils)
    when(frameworkUtils).getFramework(data).thenReturn(marathon)
    when(settings).getConfigDir().thenReturn(self.configs_dir)
    when(settings).getCliDir().thenReturn(self.base_dir)
    when(appConfig).getRogerEnv(self.configs_dir).thenReturn(roger_env)
    when(appConfig).getConfig(self.configs_dir, "app.json").thenReturn(config)
    when(appConfig).getAppData(self.configs_dir, "app.json", "grafana_test_app").thenReturn(data)

    args = self.args
    args.directory=""
    args.secrets_file=""
    args.environment="dev"
    args.skip_push=True
    args.application = 'grafana_test_app'
    args.config_file = 'app.json'
    args.skip_build = True
    args.branch = None
    os.environ["ROGER_CONFIG_DIR"] = self.configs_dir

    roger_env = appConfig.getRogerEnv(self.configs_dir)
    del roger_env['registry']
    roger_deploy.push = MagicMock(return_value=0)
    return_code = roger_deploy.main(settings, appConfig, frameworkUtils, gitObj, args)
    assert return_code == 1

  def test_roger_deploy_with_no_environment_fails(self):
    settings = mock(Settings)
    appConfig = mock(AppConfig)
    marathon = mock(Marathon)
    gitObj = mock(GitUtils)
    roger_env = self.roger_env
    config = self.config
    data = self.data
    when(marathon).getCurrentImageVersion(roger_env, 'dev', 'grafana').thenReturn("testversion/v0.1.0")
    frameworkUtils = mock(FrameworkUtils)
    when(frameworkUtils).getFramework(data).thenReturn(marathon)
    when(settings).getConfigDir().thenReturn(self.configs_dir)
    when(settings).getCliDir().thenReturn(self.base_dir)
    when(appConfig).getRogerEnv(self.configs_dir).thenReturn(roger_env)
    when(appConfig).getConfig(self.configs_dir, "app.json").thenReturn(config)
    when(appConfig).getAppData(self.configs_dir, "app.json", "grafana_test_app").thenReturn(data)

    args = self.args
    args.directory=""
    args.secrets_file=""
    args.environment=""
    args.skip_push=True
    args.application = 'grafana_test_app'
    args.config_file = 'app.json'
    args.skip_build = True
    args.branch = None
    os.environ["ROGER_CONFIG_DIR"] = self.configs_dir
    roger_deploy.push = MagicMock(return_value=0)
    return_code = roger_deploy.main(settings, appConfig, frameworkUtils, gitObj, args)
    assert return_code == 1

  def test_rogerDeploy(self):
    settings = mock(Settings)
    appConfig = mock(AppConfig)
    marathon = mock(Marathon)
    gitObj = mock(GitUtils)
    roger_env = self.roger_env
    config = self.config
    data = self.data
    when(marathon).getCurrentImageVersion(roger_env, 'dev', 'grafana').thenReturn("testversion/v0.1.0")
    frameworkUtils = mock(FrameworkUtils)
    when(frameworkUtils).getFramework(data).thenReturn(marathon)
    when(settings).getConfigDir().thenReturn(self.configs_dir)
    when(settings).getCliDir().thenReturn(self.base_dir)
    when(appConfig).getRogerEnv(self.configs_dir).thenReturn(roger_env)
    when(appConfig).getConfig(self.configs_dir, "app.json").thenReturn(config)
    when(appConfig).getAppData(self.configs_dir, "app.json", "grafana_test_app").thenReturn(data)

    args = self.args
    args.directory=""
    args.secrets_file=""
    args.environment="dev"
    args.skip_push=True
    args.application = 'grafana_test_app'
    args.config_file = 'app.json'
    args.skip_build = True
    args.branch = None
    os.environ["ROGER_CONFIG_DIR"] = self.configs_dir
    roger_deploy.push = MagicMock(return_value=0)
    roger_deploy.main(settings, appConfig, frameworkUtils, gitObj, args)
    settings.getConfigDir   = MagicMock(return_value=2)
    settings.getCliDir      = MagicMock(return_value=2)
    appConfig.getRogerEnv   = MagicMock(return_value=2)
    appConfig.getConfig     = MagicMock(return_value=2)
    verify(settings).getConfigDir()
    verify(settings).getCliDir()
    verify(appConfig).getRogerEnv(self.configs_dir)
    verify(appConfig).getConfig(self.configs_dir, "app.json")
    verify(frameworkUtils).getFramework(data)
    verify(marathon).getCurrentImageVersion(roger_env, 'dev', 'grafana_test_app')

  def tearDown(self):
    pass

if __name__ == '__main__':
  unittest.main()
