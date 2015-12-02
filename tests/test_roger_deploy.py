#!/usr/bin/python

from __future__ import print_function
import unittest
import argparse
import os
import sys
import json
sys.path.append('/vagrant/cli')
import imp
roger_deploy = imp.load_source('roger_deploy', '/vagrant/cli/roger-deploy')
roger_push = imp.load_source('roger_push', '/vagrant/cli/roger-push')
roger_git_pull = imp.load_source('roger_git_pull', '/vagrant/cli/roger-git-pull')
from marathon import Marathon
from frameworkutils import FrameworkUtils
from appconfig import AppConfig
from settings import Settings
from mockito import mock, when, verify
from mock import MagicMock

#Test basic functionalities of roger-deploy script
class TestDeploy(unittest.TestCase):

  def setUp(self):
    parser = argparse.ArgumentParser(description='Args for test')
    parser.add_argument('-e', '--environment', metavar='env',
    help="Environment to deploy to. example: 'dev' or 'stage'")
    parser.add_argument('-s', '--skip-build', action="store_true", help="Flag that skips roger-build when set to true. Defaults to false.'")
    parser.add_argument('-M', '--incr-major', action="store_true", help="Increment major in version. Defaults to false.'")
    parser.add_argument('-p', '--incr-patch', action="store_true", help="Increment patch in version. Defaults to false.'")
    parser.add_argument('-sp', '--skip-push', action="store_true", help="Flag that skips roger-push when set to true. Defaults to false.'")
    self.parser = parser
    with open('/vagrant/config/roger.json') as config:
      config = json.load(config)
    with open('/vagrant/config/roger-env.json') as roger:
      roger_env = json.load(roger)
    data = config['apps']['grafana']
    self.config = config
    self.roger_env = roger_env
    self.data = data

  def test_splitVersion(self):
    assert roger_deploy.splitVersion("0.1.0") == (0,1,0)
    assert roger_deploy.splitVersion("2.0013") == (2,13,0)
    
  def test_incrementVersion(self):
    git_sha = "dwqjdqgwd7y12edq21"
    image_version_list = ['0.001','0.2.034','1.1.2','1.002.1']
    parser = self.parser
    args = parser.parse_args()
    assert roger_deploy.incrementVersion(git_sha, image_version_list, args) == 'dwqjdqgwd7y12edq21/v1.3.0'
    args.incr_patch = True
    assert roger_deploy.incrementVersion(git_sha, image_version_list, args) == 'dwqjdqgwd7y12edq21/v1.2.2'
    args.incr_major = True
    assert roger_deploy.incrementVersion(git_sha, image_version_list, args) == 'dwqjdqgwd7y12edq21/v2.0.0'

  def test_tempDirCheck(self):
    work_dir = "./test_dir"
    roger_deploy.removeDirTree(work_dir)
    exists = os.path.exists(os.path.abspath(work_dir))
    assert exists == False
    os.makedirs(work_dir)
    exists = os.path.exists(os.path.abspath(work_dir))
    assert exists == True
    roger_deploy.removeDirTree(work_dir)
    exists = os.path.exists(os.path.abspath(work_dir))
    assert exists == False

  def test_rogerDeploy(self):
    settings = mock(Settings)
    appConfig = mock(AppConfig)
    marathon = mock(Marathon)
    roger_env = self.roger_env
    config = self.config
    data = self.data
    when(marathon).getCurrentImageVersion(roger_env, 'dev', 'grafana').thenReturn("testversion/v0.1.0")
    frameworkUtils = mock(FrameworkUtils)
    when(frameworkUtils).getFramework(data).thenReturn(marathon)
    when(settings).getConfigDir().thenReturn("/vagrant/config")
    when(settings).getCliDir().thenReturn("/vagrant")
    when(appConfig).getRogerEnv("/vagrant/config").thenReturn(roger_env)
    when(appConfig).getConfig("/vagrant/config", "roger.json").thenReturn(config)
    when(appConfig).getAppData("/vagrant/config", "roger.json", "grafana").thenReturn(data)
    parser = self.parser
    args = parser.parse_args()
    args.application = 'grafana'
    args.config_file = 'roger.json'
    args.skip_build = True
    args.branch = None
    object_list = []
    object_list.append(settings)
    object_list.append(appConfig)
    object_list.append(frameworkUtils)
    roger_deploy.push = MagicMock(return_value=0)
    roger_deploy.main(object_list, args)
    verify(settings).getConfigDir()
    verify(settings).getCliDir()
    verify(appConfig).getRogerEnv("/vagrant/config")
    verify(appConfig).getConfig("/vagrant/config", "roger.json")
    verify(frameworkUtils).getFramework(data)
    verify(marathon).getCurrentImageVersion(roger_env, 'dev', 'grafana')

  def tearDown(self):
    pass  

if __name__ == '__main__':
  unittest.main()
