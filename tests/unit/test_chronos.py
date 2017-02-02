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
        url = 'https://chronos-dev-env.place.testplace.com/scheduler/jobs/search?name=example-team'
        image_data = [{'container':{'image':'example-image/v0.1.0'}}]
        data = {'environments':{'dev':{'chronos_endpoint':'https://example-end-point.com'}}}
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
            'application-platforms-app1',
            config_dir,
            config_file,
            app_config_object
        )
        assert img == image_data[0]['container']['image']
