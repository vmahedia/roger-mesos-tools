#!/usr/bin/python

from __future__ import print_function
import unittest
import os
import json
import sys
import shutil
sys.path.insert(0,'/vagrant/cli')
from settings import Settings

#Test basic functionalities of roger-init script
class TestInit(unittest.TestCase):

  def setUp(self):
    self.settingObj = Settings()
    self.base_dir = self.settingObj.getCliDir()
    self.config_dir = self.base_dir+"/tests/configs"
    self.template_dir = self.base_dir+"/tests/templates"
    pass

  def test_roger_init(self):
    set_config_dir = ''
    if "ROGER_CONFIG_DIR" in os.environ:
      set_config_dir = os.environ.get('ROGER_CONFIG_DIR')
    os.environ["ROGER_CONFIG_DIR"] = self.config_dir

    set_templ_dir = ''
    if "ROGER_TEMPLATES_DIR" in os.environ:
      set_templ_dir = os.environ.get('ROGER_TEMPLATES_DIR')
    os.environ["ROGER_TEMPLATES_DIR"] = self.template_dir

    os.system("roger init test_app roger")
    config_file = self.config_dir+"/app.json"
    template_file = self.template_dir+"/test-app-grafana.json"
    assert os.path.exists(config_file) == True
    assert os.path.exists(template_file) == True
    with open('{0}'.format(config_file)) as config:
      config = json.load(config)
    with open('{0}'.format(template_file)) as template:
      template = json.load(template)

    assert config['name'] == "test-app"
    assert len(config['apps']) == 3
    for app in config['apps']:
      assert config['apps'][app]['name'].startswith("test_app")
      if len(config['apps'][app]['containers'])  > 0 and type(config['apps'][app]) != dict :
        assert len(config['apps'][app]['containers']) == 2
        for container in config['apps'][app]['containers']:
          assert container.startswith("container_name")
      assert config['apps'][app]['name'].startswith("test_app")

    assert template['id'] == "test-grafana"
    assert template['container']['type'] == "DOCKER"


  def tearDown(self):
    pass

if __name__ == '__main__':
  unittest.main()
