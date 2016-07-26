#!/usr/bin/python

from __future__ import print_function
import unittest
import os
import sys
import yaml
sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(os.path.realpath(__file__)), os.pardir, "cli")))
from mockito import mock, when, verify, verifyZeroInteractions
from mock import MagicMock
from slackclient import SlackClient
from mockito.matchers import any
from utils import Utils
from appconfig import AppConfig
from settings import Settings
from webhook import WebHook
# Test basic functionalities of Webhook class


class TestWebhook(unittest.TestCase):

    def setUp(self):
        self.webhook = WebHook()
        self.settingObj = Settings()
        self.base_dir = self.settingObj.getCliDir()
        self.configs_dir = self.base_dir + "/tests/configs"
        print (self.configs_dir)
        self.components_dir = self.base_dir + '/tests/components/dev'
        with open(self.configs_dir + '/roger-mesos-tools.config') as roger:
            roger_env = yaml.load(roger)
        self.roger_env = roger_env

# check for value error / exception assert
# check for one positive case - May be introduce exit code or something

    def test_invoke_webhook_when_hook_input_metrics_is_invalid(self):
        settings = mock(Settings)
        appConfig = mock(AppConfig)
        appdata = 'valid-app-data'
        hook_input_metrics = 'invalid-hook-input-metrics'
        when(settings).getConfigDir().thenReturn(self.configs_dir)
        when(appConfig).getRogerEnv(any()).thenReturn(self.roger_env)

        with self.assertRaises(ValueError):
            self.webhook.invoke_webhook(appdata, hook_input_metrics)

    def test_invoke_webhook_when_appdata_is_invalid(self):
        settings = mock(Settings)
        appConfig = mock(AppConfig)
        appdata = 'invalid-app-data'
        hook_input_metrics = 'hook-input-metrics'
        when(settings).getConfigDir().thenReturn(self.configs_dir)
        when(appConfig).getRogerEnv(any()).thenReturn(self.roger_env)

        with self.assertRaises(ValueError):
            self.webhook.invoke_webhook(appdata, hook_input_metrics)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
