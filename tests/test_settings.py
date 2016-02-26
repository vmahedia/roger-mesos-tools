#!/usr/bin/python

from __future__ import print_function
import unittest
import argparse
import os
import sys
import imp
sys.path.append('/vagrant/cli')
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
    try:
      config_dir = settingObj.getConfigDir()
    except (SystemExit) as e:
      assert ("Environment variable $ROGER_CONFIG_DIR is not set. Exiting." in e)
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
    try:
      comp_dir = settingObj.getComponentsDir()
    except (SystemExit) as e:
      assert ("Environment variable $ROGER_COMPONENTS_DIR is not set. Exiting." in e)
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
    try:
      temp_dir = settingObj.getTemplatesDir()
    except (SystemExit) as e:
      assert ("Environment variable $ROGER_TEMPLATES_DIR is not set.Exiting." in e)
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
    try:
      sect_dir = settingObj.getSecretsDir()
    except (SystemExit) as e:
      assert ("Environment variable $ROGER_SECRETS_DIR is not set. Exiting." in e)
    if set_sect_dir.strip() != '':
      os.environ["ROGER_SECRETS_DIR"] = "{}".format(set_sect_dir)

  def test_getCliDir(self):
    set_cli_dir = ''
    cli_dir = settingObj.getCliDir()
    assert cli_dir is not None

  def tearDown(self):
    pass

if __name__ == '__main__':
  settingObj = Settings()
  unittest.main()
