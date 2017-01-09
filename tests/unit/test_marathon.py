#!/usr/bin/python

from __future__ import print_function
import unittest
import os
import sys
import requests
sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(os.path.realpath(__file__)), os.pardir, "cli")))
from cli.marathon import Marathon
from cli.appconfig import AppConfig
from mockito import mock, when

# Test basic functionalities of MarathonValidator class


class TestMarathon(unittest.TestCase):

    def setUp(self):
        self.marathon = Marathon()
        self.appconfig = AppConfig()

    def test_validateGroupDetails(self):
        group_details = {}
        message_list = []
        group_details['/test/app1'] = ('/http_prefix1', ['3000', '3001'], False)
        group_details['/test/app2'] = ('/http_prefix2', ['9000', '9001'], False)
        valid = self.marathon.validateGroupDetails(group_details, message_list)
        assert valid is True
        assert len(message_list) == 0
        message_list = []
        group_details['/test/app3'] = ('/http_prefix3', ['8000', '9001'], False)
        valid = self.marathon.validateGroupDetails(group_details, message_list)
        assert valid is False
        assert len(message_list) == 1
        message_list = []
        group_details = {}
        group_details['/test/app3'] = ('/http_prefix3', ['8000', '9001'], False)
        group_details['/test/app4'] = ('/http_prefix3', ['7000', '7001'], False)
        valid = self.marathon.validateGroupDetails(group_details, message_list)
        assert valid is False
        assert len(message_list) == 1
        message_list = []
        group_details = {}
        # One of the conflicting apps have affinity = False, leads to a failed
        # validation for HTTP_PREFIX
        group_details['/test/app3'] = ('/http_prefix3', ['9000', '9001'], False)
        group_details['/test/app5'] = ('/http_prefix3', ['8000', '8001'], True)
        valid = self.marathon.validateGroupDetails(group_details, message_list)
        assert valid is False
        assert len(message_list) == 1
        message_list = []
        group_details = {}
        group_details['/test/app3'] = ('/http_prefix3', ['9000', '9001'], True)
        group_details['/test/app5'] = ('/http_prefix3', ['8000', '8001'], True)
        valid = self.marathon.validateGroupDetails(group_details, message_list)
        assert valid is True
        assert len(message_list) == 1
        for message in message_list:
            print(message)

    @property
    def config_dir(self):
        os.environ['ROGER_CONFIG_DIR'] = '/vagrant/config'

    def test_get_image(self):
        url = 'https://marathon-dev-roger.dal.moz.com/v2/apps/welcome'

        data = {'dev':{'marathon_endpoint':'https://marathon-dev-roger.dal.moz.com'}}
        image_data = {'app':{'container':{'docker':{'image':"registry.roger.dal.moz.com:5000/moz-roger-welcome-2522615506470f3d148509f913047060f08ecb64/v0.72.0"}}}}
        os.environ['ROGER_CONFIG_DIR'] = '/vagrant/config'
        username = 'first.first'
        password = 'last.last'
        config_dir = '/vagrant/config'
        config_file = 'test.yml'

        app_config_object = mock(AppConfig)
        when(app_config_object).getConfig(config_dir, config_file).thenReturn(data)
        when(requests).get(url, auth=(username, password)).thenReturn(image_data)

        m = Marathon()
        img = m.image_name(
            username,
            password,
            'dev',
            'welcome',
            config_dir,
            config_file,
            app_config_object
        )
        assert img == image_data['app']['container']['docker']['image']

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
