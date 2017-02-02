#!/usr/bin/python

from __future__ import print_function
import unittest
import os
import sys
import requests
import json
from cli.chronos import Chronos
from cli.marathon import Marathon
from cli.framework import Framework
from cli.appconfig import AppConfig
from cli.utils import Utils
from mockito import mock, when
utils = Utils()


class TestChronos(unittest.TestCase):
    def setUp(self):
        self.marathon = Marathon()
        self.appconfig = AppConfig()

    def test_image_name(self):
        res = mock(requests.Response)
        url = 'https://example/scheduler/jobs/search?name=example_team-app'
        image_data = [{'container':{'image':'moz-roger-simpleapp-1abd568915ad7598a37d1564b103b5b3dc8d9507/v0.1.0'}}]
        data = {'environments':{'dev':{'chronos_endpoint':'https://example'}}}
        os.environ['ROGER_CONFIG_DIR'] = '/vagrant/config'
        username = 'first.first'
        password = 'last.last'
        config_dir = '/vagrant/config'
        config_file = 'test.yml'

        app_config_object = mock(AppConfig)
        when(app_config_object).getRogerEnv(config_dir).thenReturn(data)
        when(requests).get(url, auth=(username, password)).thenReturn(res)
        when(res).json().thenReturn(image_data)

        c = Chronos()
        img = c.get_image_name(
            username,
            password,
            'dev',
            'example_team-app',
            config_dir,
            config_file,
            app_config_object
        )
        assert img == image_data[0]['container']['image']
