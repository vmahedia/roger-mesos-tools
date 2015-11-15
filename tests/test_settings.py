#!/usr/bin/python

from __future__ import print_function
import unittest
import argparse
import os
import sys
import imp
sys.path.append('/vagrant/bin')
from settings import Settings

#Test basic functionalities of Settings class
class TestSettings(unittest.TestCase):

  def setUp(self):
    pass

  def test_getConfigDir(self):
    set_config_dir = ''
    if "ROGER_CONFIG_DIR" in os.environ:
      set_config_dir = os.environ.get('ROGER_CONFIG_DIR')
    os.environ["ROGER_CONFIG_DIR"] = "/vagrant/testconfigdir"
    config_dir = settingObj.getConfigDir()
    assert config_dir == "/vagrant/testconfigdir"
    del os.environ['ROGER_CONFIG_DIR']
    config_dir = settingObj.getConfigDir()
    assert config_dir == ''
    if set_config_dir.strip() != '':
      os.environ["ROGER_CONFIG_DIR"] = "{}".format(set_config_dir)

  def test_getComponentsDir(self):
    set_comp_dir = ''
    if "ROGER_COMPONENTS_DIR" in os.environ:
      set_comp_dir = os.environ.get('ROGER_COMPONENTS_DIR')
    os.environ["ROGER_COMPONENTS_DIR"] = "/vagrant/testcompdir"
    comp_dir = settingObj.getComponentsDir()
    assert comp_dir == "/vagrant/testcompdir"
    del os.environ['ROGER_COMPONENTS_DIR']
    comp_dir = settingObj.getComponentsDir()
    assert comp_dir == ''
    if set_comp_dir.strip() != '':
      os.environ["ROGER_COMPONENTS_DIR"] = "{}".format(set_comp_dir)

  def test_getTemplatesDir(self):
    set_temp_dir = ''
    if "ROGER_TEMPLATES_DIR" in os.environ:
      set_temp_dir = os.environ.get('ROGER_TEMPLATES_DIR')
    os.environ["ROGER_TEMPLATES_DIR"] = "/vagrant/testtempldir"
    temp_dir = settingObj.getTemplatesDir()
    assert temp_dir == "/vagrant/testtempldir"
    del os.environ['ROGER_TEMPLATES_DIR']
    temp_dir = settingObj.getTemplatesDir()
    assert temp_dir == ''
    if set_temp_dir.strip() != '':
      os.environ["ROGER_TEMPLATES_DIR"] = "{}".format(set_temp_dir)

  def test_getSecretsDir(self):
    set_sect_dir = ''
    if "ROGER_SECRETS_DIR" in os.environ:
      set_sect_dir = os.environ.get('ROGER_SECRETS_DIR')
    os.environ["ROGER_SECRETS_DIR"] = "/vagrant/testsectdir"
    sect_dir = settingObj.getSecretsDir()
    assert sect_dir == "/vagrant/testsectdir"
    del os.environ['ROGER_SECRETS_DIR']
    sect_dir = settingObj.getSecretsDir()
    assert sect_dir == ''
    if set_sect_dir.strip() != '':
      os.environ["ROGER_SECRETS_DIR"] = "{}".format(set_sect_dir)

  def tearDown(self):
    pass

if __name__ == '__main__':
  settingObj = Settings()
  unittest.main()
