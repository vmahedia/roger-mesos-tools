# -*- encoding: utf-8 -*-

"""
Unit test for roger_promote.py

"""

import tests.helper

import unittest
import os
import os.path
import pytest
import requests

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
        self.marathon = mock(Marathon)
        self.settings = mock(Settings)
        self.app_config = mock(AppConfig)
        self.framework = self.marathon
        self.framework_utils = mock(FrameworkUtils)
        self.config_file = "test.yml"
        self.roger_env = {}
        os.environ['ROGER_CONFIG_DIR'] = '/vagrant/config'

    @property
    def config_dir(self):
        return os.environ['ROGER_CONFIG_DIR']

    def test_config_dir(self):

        rp = RogerPromote()
        assert rp.config_dir == '/vagrant/config'

    def test_roger_env(self):

        fake_config = tests.helper.fake_config()
        settings = mock(Settings)

        when(self.app_config).getRogerEnv(
            self.config_dir
        ).thenReturn(fake_config)

        rp = RogerPromote(app_config=self.app_config)
        assert rp.roger_env == fake_config

    def test_set_framework(self):
        app_data = {'test_app': {'name': 'test_app'}}

        when(self.app_config).getAppData(
            self.config_dir, self.config_file, 'test_app'
        ).thenReturn(app_data)

        rp = RogerPromote(app_config=self.app_config)

        rp._set_framework(self.config_file, 'test_app')

        assert rp._framework.getName() == 'Marathon'

    def test_image_name(self):
        os.environ['ROGER_USER'] = "first.last"
        os.environ['ROGER_USER_PASS_DEV'] = "password"
        os.environ['ROGER_USER_PASS_STAGE'] = "password"
        os.environ['ROGER_USER_PASS_PROD'] = "password"

        framework = mock(Marathon)

        when(framework).getName().thenReturn("Marathon")
        when(framework).app_id(
            "test_path/test_app.json",
            "Marathon"
        ).thenReturn("app_id")
        when(framework).image_name(
            'first.last',
            "password",
            "dev",
            "app_id",
            self.config_dir,
            self.config_file
        ).thenReturn("test_image")

        rp = RogerPromote(framework=framework)
        assert rp._image_name(
            'dev',
            self.config_file,
            "test_path/test_app.json") == 'test_image'

    def test_config_resolver(self):
        framework = mock(Framework)
        settings = mock(Settings)
        app_config = mock(AppConfig)
        config_dir = '/vagrant/config'
        fake_team_config = tests.helper.fake_team_config()

        when(settings).getConfigDir().thenReturn(config_dir)
        when(app_config).getConfig(
            config_dir, 'roger.json'
        ).thenReturn(fake_team_config)

        rp = RogerPromote(settings=settings, app_config=app_config)
        val = rp._config_resolver('template_path', 'test_app', 'roger.json')
        assert val == 'framework_template_path'

    def test_roger_push_script(self):
        path = RogerPromote()._roger_push_script()
        assert 'roger-mesos-tools/cli/roger_push.py' in path
