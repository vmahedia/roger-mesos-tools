# -*- encoding: utf-8 -*-

"""
Integration tests for roger_promote.py

:Classes:

TestPromote
"""
import tests.helper
# ~
# stdlib
import unittest
import os
import json

# ~
# pip installed
from mockito import mock, Mock, when
import requests

# ~
# core
from cli.roger_promote import RogerPromote
from cli.appconfig import AppConfig
from cli.settings import Settings


class TestRogerPromote(unittest.TestCase):
    def setUp(self):
        self.settings = mock(Settings)
        self.app_config = mock(AppConfig)

    def settings_and_config(self, data):
        when(self.settings).getConfigDir().thenReturn('/vagrant/config')
        when(self.app_config).getConfig(
            '/vagrant/config', 'test.yml'
        ).thenReturn(data)
        return (settings, app_config)

    @property
    def config_dir(self):
        os.environ['ROGER_CONFIG_DIR'] = '/vagrant/config'
        return os.environ['ROGER_CONFIG_DIR']

    def test_deploy_app(self):
        headers = {'Content-Type': 'application/json'}
        # data = {
        #     "container": {
        #         "type": "DOCKER",
        #         "docker": {
        #             "network": "BRIDGE",
        #             "image": "ubuntu:14.04"
        #         }
        #     },
        #     "cpus": 0.1,
        #     "mem": 5
        # }
        data = {
            "cmd": "sleep 55",
            "cpus": "0.3",
            "instances": "2",
            "mem": "9",
            "ports": [
                9000
            ]
        }
        r = requests.put(
            'http://localmesos01:8080/v2/apps/test_app',
            data=data,
            headers=headers
        )

        # if not r.status_code == requests.codes.ok:
        #     raise requests.exceptions.HTTPError

        assert json.loads(r.text) == ''
