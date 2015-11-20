#!/usr/bin/python

from __future__ import print_function
import unittest
import argparse
import os
import sys
import imp
sys.path.append('/vagrant/cli')
from appconfig import AppConfig

#Test basic functionalities of Settings class
class TestSettings(unittest.TestCase):

  def setUp(self):
    pass

  def test_getRogerEnv(self):
    roger_env = appObj.getRogerEnv("/vagrant/tests/configs")
    assert roger_env['registry'] == "registry.roger.dal.moz.com:5000"
    assert roger_env['default'] == "dev"
    assert roger_env['environments']['dev']['marathon_endpoint'] == "http://daldevmesoszk01:8080"
    assert roger_env['environments']['prod']['chronos_endpoint'] == "http://dalmesoszk01:4400" 

  def test_getConfig(self):
    config = appObj.getConfig("/vagrant/tests/configs", "app.json")
    assert config['name'] == "test-app"
    assert config['repo'] == "roger"
    assert config['vars']['environment']['prod']['mem'] == "2048"
    assert len(config['apps'].keys()) == 1
    for app in config['apps']:
      assert app == "test_app"
      assert config['apps'][app]['imageBase'] == "test_app_base"

  def test_getAppData(self):
    app_data = appObj.getAppData("/vagrant/tests/configs", "app.json", "app_name")
    assert app_data == ''
    app_data = appObj.getAppData("/vagrant/tests/configs", "app.json", "test_app")
    assert app_data['imageBase'] == "test_app_base"
    assert len(app_data['containers']) == 2

  def tearDown(self):
    pass

if __name__ == "__main__":
  appObj = AppConfig()
  unittest.main()
