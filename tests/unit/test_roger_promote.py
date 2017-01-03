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
        self.marathon = mock(Marathon)
        self.settings = mock(Settings)
        self.app_config = mock(AppConfig)
        self.framework = self.marathon
        self.framework_utils = mock(FrameworkUtils)
        self.config_file = "test.yml"
        self.roger_env = {}

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
        data = {
            "apps": {
                "test_app": {
                    "path": "dockerfile_path",
                    "containers": [
                        "test_app"
                    ],
                    "name": "test_app",
                    "vars": {
                        "environment": {
                            "prod": {},
                            "dev": {},
                            "stage": {}
                        },
                        "global": {}
                    },
                    "template_path": "framework_template_path"
                }
            }
        }

        when(self.framework).getCurrentImageVersion(
            data, 'stage', 'testApp'
        ).thenReturn("imageName")

        rp = RogerPromote(framework=mock(Marathon))
        assert rp._image_name('stage', 'testApp') == 'imageName'

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

    def test_config_resolver(self):
        # Fakes
        settings = mock(Settings)
        app_config = mock(AppConfig)
        config_dir = '/vagrant/config'
        fake_team_config = tests.helper.fake_team_config()

        # Stubs
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
