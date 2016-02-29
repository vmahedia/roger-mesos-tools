#!/usr/bin/python

from __future__ import print_function
import unittest
import os
import json
import sys
sys.path.append('/vagrant/bin')
import shutil
import imp

#Test basic functionalities of roger-init script
class TestInit(unittest.TestCase):

  def setUp(self):
    pass

  def test_roger_init(self):
    set_config_dir = ''
    if "ROGER_CONFIG_DIR" in os.environ:
      set_config_dir = os.environ.get('ROGER_CONFIG_DIR')
    os.environ["ROGER_CONFIG_DIR"] = "/vagrant/tests/configs"

    set_templ_dir = ''
    if "ROGER_TEMPLATES_DIR" in os.environ:
      set_templ_dir = os.environ.get('ROGER_TEMPLATES_DIR')
    os.environ["ROGER_TEMPLATES_DIR"] = "/vagrant/configs/templates"

    os.system("roger init test_app roger")
    config_file = "/vagrant/tests/configs/app.json"
    template_file = "/vagrant/tests/templates/test-app-grafana.json"
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
