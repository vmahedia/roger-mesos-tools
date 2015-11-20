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
    os.environ["ROGER_CONFIG_DIR"] = "/vagrant/configdir"
    
    set_templ_dir = ''
    if "ROGER_TEMPLATES_DIR" in os.environ:
      set_templ_dir = os.environ.get('ROGER_TEMPLATES_DIR')
    os.environ["ROGER_TEMPLATES_DIR"] = "/vagrant/templdir"

    os.system("roger init test_app roger")
    config_file = "/vagrant/configdir/roger.json"
    template_file = "/vagrant/templdir/roger-test_app.json"
    assert os.path.exists(config_file) == True
    assert os.path.exists(template_file) == True
    with open('{0}'.format(config_file)) as config:
      config = json.load(config)
    with open('{0}'.format(template_file)) as template:
      template = json.load(template)

    assert config['name'] == "roger"
    assert len(config['apps']) == 1
    for app in config['apps']:
      assert app == "test_app"
      assert len(config['apps'][app]['containers']) == 1
      for container in config['apps'][app]['containers']:
        assert container == "test_app"
      assert config['apps'][app]['name'] == "test_app"

    assert template['id'] == "roger-test_app"
    assert template['container']['type'] == "DOCKER"
    
    shutil.rmtree("/vagrant/configdir")
    shutil.rmtree("/vagrant/templdir")
    if set_config_dir.strip() != '':
      os.environ["ROGER_CONFIG_DIR"] = "{}".format(set_config_dir)
    if set_templ_dir.strip() != '':
      os.environ["ROGER_TEMPLATES_DIR"] = "{}".format(set_templ_dir)

  def tearDown(self):
    pass

if __name__ == '__main__':
  unittest.main()
