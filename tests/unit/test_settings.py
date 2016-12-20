#!/usr/bin/python

from __future__ import print_function
import unittest
import argparse
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(os.path.realpath(__file__)), os.pardir, "cli")))
from cli.settings import Settings

# Test basic functionalities of Settings class


class TestSettings(unittest.TestCase):

    def setUp(self):
        self.settingObj = Settings()
        self.base_dir = self.settingObj.getCliDir()

    def test_getConfigDir(self):
        set_config_dir = ''
        if "ROGER_CONFIG_DIR" in os.environ:
            set_config_dir = os.environ.get('ROGER_CONFIG_DIR')
        os.environ["ROGER_CONFIG_DIR"] = self.base_dir + "/testconfigdir"
        config_dir = self.settingObj.getConfigDir()
        assert config_dir == self.base_dir + "/testconfigdir"
        del os.environ['ROGER_CONFIG_DIR']
        try:
            config_dir = self.settingObj.getConfigDir()
        except (ValueError) as e:
            assert (
                "Environment variable $ROGER_CONFIG_DIR is not set." in e)
        if set_config_dir.strip() != '':
            os.environ["ROGER_CONFIG_DIR"] = "{}".format(set_config_dir)

    def test_getComponentsDir(self):
        set_comp_dir = ''
        if "ROGER_COMPONENTS_DIR" in os.environ:
            set_comp_dir = os.environ.get('ROGER_COMPONENTS_DIR')
        os.environ["ROGER_COMPONENTS_DIR"] = self.base_dir + "/testcompdir"
        comp_dir = self.settingObj.getComponentsDir()
        assert comp_dir == self.base_dir + "/testcompdir"
        del os.environ['ROGER_COMPONENTS_DIR']
        try:
            comp_dir = self.settingObj.getComponentsDir()
        except (ValueError) as e:
            assert (
                "Environment variable $ROGER_COMPONENTS_DIR is not set." in e)
        if set_comp_dir.strip() != '':
            os.environ["ROGER_COMPONENTS_DIR"] = "{}".format(set_comp_dir)

    def test_getTemplatesDir(self):
        set_temp_dir = ''
        if "ROGER_TEMPLATES_DIR" in os.environ:
            set_temp_dir = os.environ.get('ROGER_TEMPLATES_DIR')
        os.environ["ROGER_TEMPLATES_DIR"] = self.base_dir + "/testtempldir"
        temp_dir = self.settingObj.getTemplatesDir()
        assert temp_dir == self.base_dir + "/testtempldir"
        del os.environ['ROGER_TEMPLATES_DIR']
        try:
            temp_dir = self.settingObj.getTemplatesDir()
        except (ValueError) as e:
            assert (
                "Environment variable $ROGER_TEMPLATES_DIR is not set." in e)
        if set_temp_dir.strip() != '':
            os.environ["ROGER_TEMPLATES_DIR"] = "{}".format(set_temp_dir)

    def test_getSecretsDir(self):
        set_sect_dir = ''
        if "ROGER_SECRETS_DIR" in os.environ:
            set_sect_dir = os.environ.get('ROGER_SECRETS_DIR')
        os.environ["ROGER_SECRETS_DIR"] = self.base_dir + "/testsectdir"
        sect_dir = self.settingObj.getSecretsDir()
        assert sect_dir == self.base_dir + "/testsectdir"
        del os.environ['ROGER_SECRETS_DIR']
        try:
            sect_dir = self.settingObj.getSecretsDir()
        except (ValueError) as e:
            assert (
                "Environment variable $ROGER_SECRETS_DIR is not set." in e)
        if set_sect_dir.strip() != '':
            os.environ["ROGER_SECRETS_DIR"] = "{}".format(set_sect_dir)

    def test_getCliDir(self):
        set_cli_dir = ''
        cli_dir = self.settingObj.getCliDir()
        assert cli_dir is not None

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
