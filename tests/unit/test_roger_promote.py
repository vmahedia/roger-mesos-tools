# -*- encoding: utf-8 -*-

"""
Unit test for roger_promote.py

"""

import tests.helper

import unittest
import os
import os.path
import pytest


from mockito import mock, Mock, when


from cli.roger_promote import RogerPromote
from cli.appconfig import AppConfig
from cli.settings import Settings
from cli.framework import Framework
from cli.frameworkUtils import FrameworkUtils


class TestRogerPromote(unittest.TestCase):
    def setUp(self):
        self.settings = mock(Settings)
        self.app_config = mock(AppConfig)
        self.framework = mock(Framework)
        self.framework_utils = mock(FrameworkUtils)
        self.config_file = "test.yml"

    @property
    def config_dir(self):
        os.environ['ROGER_CONFIG_DIR'] = '/vagrant/config'
        return os.environ['ROGER_CONFIG_DIR']

    def behavior_with_config_data(self, data):
        when(self.app_config).getRogerEnv('/vagrant/config').thenReturn(data)

    def test_config_dir(self):
        os.environ['ROGER_CONFIG_DIR'] = '/vagrant/config'
        when(self.settings).getConfigDir().thenReturn('/vagrant/config')
        rp = RogerPromote()
        assert rp.config_dir == '/vagrant/config'

    def test_roger_env(self):
        when(self.app_config).getRogerEnv(self.config_dir).thenReturn({})
        rp = RogerPromote(app_config=self.app_config)
        assert rp.roger_env is None

    def test_set_framework(self):
        # app_data is a dict taken from the config file for a given app
        app_data = {'test_app': {'name': 'test_app'}}
        # only stub the getAppData call
        when(self.app_config).getAppData(
            self.config_dir, self.config_file, 'test_app'
        ).thenReturn(app_data)
        # Pass in the fake app_config instance
        rp = RogerPromote(app_config=self.app_config)
        # Call the method to set the framework
        rp._set_framework(self.config_file, 'test_app')
        # Get the framework name by calling getName() on the object. It should
        # default to Marathon since we didn't set the framework key in the data
        # var
        assert rp._framework.getName() == 'Marathon'

    # def test_image_name(self):
    #     when(self.framework).getCurrentImageVersion().thenReturn(' ')
    #     rp = RogerPromote(framework=self.framework)
    #     assert rp._image_name('stage', 'appName') == ' '
