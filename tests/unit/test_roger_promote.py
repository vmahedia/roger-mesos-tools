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
from cli.marathon import Marathon
from cli.chronos import Chronos


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

    def test_config_dir(self):
        os.environ['ROGER_CONFIG_DIR'] = '/vagrant/config'

        # Stubs
        when(self.settings).getConfigDir().thenReturn('/vagrant/config')

        # Instance
        rp = RogerPromote()
        assert rp.config_dir == '/vagrant/config'

    def test_roger_env(self):
        # Fakes
        fake_config = tests.helper.fake_config()
        settings = mock(Settings)

        # Stubs
        when(settings).getConfigDir().thenReturn('/vagrant/config')
        when(self.app_config).getRogerEnv(
            self.config_dir
        ).thenReturn(fake_config)

        # Instance
        rp = RogerPromote(app_config=self.app_config)
        assert rp.roger_env == fake_config

    def test_set_framework(self):
        # app_data is a dict taken from the config file for a given app
        app_data = {'test_app': {'name': 'test_app'}}

        # Stubs
        when(self.app_config).getAppData(
            self.config_dir, self.config_file, 'test_app'
        ).thenReturn(app_data)

        # Instance
        rp = RogerPromote(app_config=self.app_config)

        # Call the method to set the framework
        rp._set_framework(self.config_file, 'test_app')
        # Get the framework name by calling getName() on the object. It should
        # default to Marathon since we didn't set the framework key in the data
        # var
        assert rp._framework.getName() == 'Marathon'

    def test_image_name(self):
        # Fakes
        framework = mock(Marathon)
        app_config = mock(AppConfig)
        settings = mock(Settings)
        fake_config = tests.helper.fake_config()

        # Stubs
        when(settings).getConfigDir().thenReturn('/vagrant/config')
        when(app_config).getRogerEnv('/vagrant/config').thenReturn(fake_config)
        when(framework).getCurrentImageVersion(
            fake_config,
            'stage',
            'TestApp'
        ).thenReturn('test_image')

        # Get instance
        rp = RogerPromote(
            settings=settings,
            app_config=app_config,
            framework=framework
        )
        assert rp._image_name('stage', 'TestApp') == 'test_image'
