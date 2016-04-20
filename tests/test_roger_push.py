#!/usr/bin/python

from __future__ import print_function
import unittest
import os
import argparse
import json
import sys
sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(os.path.realpath(__file__)), os.pardir, "cli")))
from roger_push import RogerPush
from marathon import Marathon
from frameworkUtils import FrameworkUtils
from appconfig import AppConfig
from settings import Settings
from mockito import mock, when, verify, verifyZeroInteractions
from mock import MagicMock
from mockito.matchers import any
from settings import Settings
from hooks import Hooks

# Test basic functionalities of roger-push script


class TestPush(unittest.TestCase):

    def setUp(self):
        parser = argparse.ArgumentParser(description='Args for test')
        parser.add_argument('-e', '--env', metavar='env',
                            help="Environment to deploy to. example: 'dev' or 'stage'")
        parser.add_argument(
            '--skip-push', '-s', help="Don't push. Only generate components. Defaults to false.", action="store_true")
        parser.add_argument(
            '--secrets-file', '-S', help="Specify an optional secrets file for deploy runtime variables.")
        self.parser = parser
        self.args = parser

        self.settingObj = Settings()
        self.base_dir = self.settingObj.getCliDir()
        self.configs_dir = self.base_dir + "/tests/configs"
        self.components_dir = self.base_dir + '/tests/components/dev'

        config = {u'repo': u'roger', u'notifications': {u'username': u'Roger Deploy', u'method': u'chat.postMessage', u'channel': u'Channel ID', u'emoji': u':rocket:'},
                  u'apps': {u'test_app': {u'imageBase': u'test_app_base', u'name': u'test_app', u'containers': [u'container_name1', u'container_name2']},
                            u'test_app1': {u'framework': u'chronos', u'name': u'test_app1', u'containers': [u'container_name1', u'container_name2'], u'imageBase': u'test_app_base'},
                            u'grafana_test_app': {u'imageBase': u'test_app_base', u'name': u'test_app_grafana', u'containers': [u'grafana', {u'grafana1': {u'vars': {u'environment': {u'prod': {u'mem': u'2048', u'cpus': u'2'}, u'dev': {u'mem': u'512', u'cpus': u'0.5'}},
                                                                                                                                                                     u'global': {u'mem': u'128', u'cpus': u'0.1'}}}}, {u'grafana2': {u'vars': {u'environment': {u'prod': {u'mem': u'2048', u'cpus': u'2'},
                                                                                                                                                                                                                                                                u'dev': {u'mem': u'1024', u'cpus': u'1'}}, u'global': {u'mem': u'128', u'cpus': u'0.1'}}}}]}}, u'name': u'test-app',
                  u'vars': {u'environment': {u'prod': {u'mem': u'2048', u'cpus': u'2'}, u'dev': {u'mem': u'512', u'cpus': u'1'},
                                             u'stage': {u'mem': u'1024', u'cpus': u'1'}}, u'global': {u'instances': u'1', u'network': u'BRIDGE'}}}

        with open(self.configs_dir + '/roger-env.json') as roger:
            roger_env = json.load(roger)
        data = config['apps']['grafana_test_app']
        self.config = config
        self.roger_env = roger_env
        self.data = data
        test_config = config
        test_data = test_config['apps']['grafana_test_app']
        self.test_config = test_config
        self.test_data = test_data

    def test_roger_push_grafana_test_app(self):
        settings = mock(Settings)
        appConfig = mock(AppConfig)
        roger_push = RogerPush()
        marathon = mock(Marathon)
        mockedHooks = mock(Hooks)
        when(mockedHooks).run_hook(any(), any(), any()).thenReturn(0)
        roger_env = self.roger_env
        config = self.config
        data = self.data
        when(marathon).put(any(), any(), any()).thenReturn("Response [200]")
        frameworkUtils = mock(FrameworkUtils)
        when(frameworkUtils).getFramework(data).thenReturn(marathon)
        when(settings).getComponentsDir().thenReturn(
            self.base_dir + "/tests/components")
        when(settings).getSecretsDir().thenReturn(
            self.base_dir + "/tests/secrets")
        when(settings).getTemplatesDir().thenReturn(
            self.base_dir + "/tests/templates")
        when(settings).getConfigDir().thenReturn(self.configs_dir)
        when(settings).getCliDir().thenReturn(self.base_dir)
        when(appConfig).getRogerEnv(any()).thenReturn(roger_env)
        when(appConfig).getConfig(any(), any()).thenReturn(config)
        when(appConfig).getAppData(any(), any(), any()).thenReturn(data)

        args = self.args
        args.env = "dev"
        args.secrets_file = ""
        args.skip_push = True
        args.app_name = 'grafana_test_app'
        args.config_file = 'test.json'
        args.directory = self.base_dir + '/tests/testrepo'
        args.image_name = 'grafana/grafana:2.1.3'
        roger_push.main(settings, appConfig, frameworkUtils, mockedHooks, args)
        with open(self.base_dir + '/tests/templates/test-app-grafana.json') as output:
            output = json.load(output)
        assert output['container']['docker'][
            'image'] == "grafana/grafana:2.1.3"
        verify(settings).getConfigDir()
        verify(settings).getComponentsDir()
        verify(settings).getTemplatesDir()
        verify(settings).getSecretsDir()
        verify(frameworkUtils).getFramework(data)

    def test_container_resolution(self):
        settings = mock(Settings)
        appConfig = mock(AppConfig)
        roger_push = RogerPush()
        marathon = mock(Marathon)
        mockedHooks = mock(Hooks)
        when(mockedHooks).run_hook(any(), any(), any()).thenReturn(0)
        roger_env = self.roger_env
        config = self.test_config
        data = self.test_data
        when(marathon).put(any(), any(), any()).thenReturn("Response [200]")
        when(marathon).put(any(), any(), any()).thenReturn("Response [200]")
        when(marathon).put(any(), any(), any()).thenReturn("Response [200]")
        frameworkUtils = mock(FrameworkUtils)
        when(frameworkUtils).getFramework(data).thenReturn(marathon)
        when(settings).getComponentsDir().thenReturn(
            self.base_dir + "/tests/components")
        when(settings).getSecretsDir().thenReturn(
            self.base_dir + "/tests/secrets")
        when(settings).getTemplatesDir().thenReturn(
            self.base_dir + "/tests/templates")
        when(settings).getConfigDir().thenReturn(self.configs_dir)
        when(settings).getCliDir().thenReturn(self.base_dir)
        when(appConfig).getRogerEnv(self.configs_dir).thenReturn(roger_env)
        when(appConfig).getConfig(any(), any()).thenReturn(config)
        when(appConfig).getAppData(any(), any(), any()).thenReturn(data)

        args = self.args
        args.env = "dev"
        args.secrets_file = ""
        args.skip_push = True
        args.app_name = 'grafana_test_app'
        args.directory = self.base_dir + '/tests/testrepo'
        args.config_file = 'test.json'
        args.image_name = 'grafana/grafana:2.1.3'
        roger_push.main(settings, appConfig, frameworkUtils, mockedHooks, args)
        with open(self.base_dir + '/tests/templates/test-app-grafana.json') as output:
            output = json.load(output)
        assert output['container']['docker'][
            'image'] == "grafana/grafana:2.1.3"
        assert output['cpus'] == 2
        assert output['mem'] == 1024
        assert output['uris'] == ["abc", "xyz", "$ENV_VAR"]
        with open(self.base_dir + '/tests/templates/test-app-grafana1.json') as output:
            output = json.load(output)
        assert output['container']['docker'][
            'image'] == "grafana/grafana:2.1.3"
        assert output['cpus'] == 0.5
        assert output['mem'] == 512
        with open(self.base_dir + '/tests/templates/test-app-grafana2.json') as output:
            output = json.load(output)
        assert output['container']['docker'][
            'image'] == "grafana/grafana:2.1.3"
        assert output['cpus'] == 1
        assert output['mem'] == 1024

    def test_roger_push_with_no_app_fails(self):
        settings = mock(Settings)
        appConfig = mock(AppConfig)
        roger_push = RogerPush()
        marathon = mock(Marathon)
        mockedHooks = mock(Hooks)
        when(mockedHooks).run_hook(any(), any(), any()).thenReturn(0)
        roger_env = self.roger_env
        config = self.config
        data = self.data
        when(marathon).put(any(), any(), any()).thenReturn("Response [200]")
        frameworkUtils = mock(FrameworkUtils)
        when(frameworkUtils).getFramework(data).thenReturn(marathon)
        when(settings).getComponentsDir().thenReturn(
            self.base_dir + "/tests/components")
        when(settings).getSecretsDir().thenReturn(
            self.base_dir + "/tests/secrets")
        when(settings).getTemplatesDir().thenReturn(
            self.base_dir + "/tests/templates")
        when(settings).getConfigDir().thenReturn(self.configs_dir)
        when(settings).getCliDir().thenReturn(self.base_dir)
        when(appConfig).getRogerEnv(any()).thenReturn(roger_env)
        when(appConfig).getConfig(any(), any()).thenReturn(config)
        when(appConfig).getAppData(any(), any(), any()).thenReturn(data)

        args = self.args
        args.app_name = ''
        args.config_file = 'test.json'
        args.env = 'some_test_env'
        with self.assertRaises(ValueError):
            roger_push.main(settings, appConfig,
                            frameworkUtils, mockedHooks, args)

    def test_roger_push_with_no_registry_fails(self):
        settings = mock(Settings)
        appConfig = mock(AppConfig)
        roger_push = RogerPush()
        marathon = mock(Marathon)
        mockedHooks = mock(Hooks)
        when(mockedHooks).run_hook(any(), any(), any()).thenReturn(0)
        roger_env = self.roger_env
        config = self.config
        data = self.data
        when(marathon).put(any(), any(), any()).thenReturn("Response [200]")
        frameworkUtils = mock(FrameworkUtils)
        when(frameworkUtils).getFramework(data).thenReturn(marathon)
        when(settings).getComponentsDir().thenReturn(
            self.base_dir + "/tests/components")
        when(settings).getSecretsDir().thenReturn(
            self.base_dir + "/tests/secrets")
        when(settings).getTemplatesDir().thenReturn(
            self.base_dir + "/tests/templates")
        when(settings).getConfigDir().thenReturn(self.configs_dir)
        when(settings).getCliDir().thenReturn(self.base_dir)
        when(appConfig).getRogerEnv(any()).thenReturn(roger_env)
        when(appConfig).getConfig(any(), any()).thenReturn(config)
        when(appConfig).getAppData(any(), any(), any()).thenReturn(data)

        args = self.args
        args.env = "dev"
        args.secrets_file = ""
        args.skip_push = True
        args.app_name = 'grafana_test_app'
        args.config_file = 'test.json'
        args.directory = self.base_dir + '/tests/testrepo'
        args.image_name = 'grafana/grafana:2.1.3'

        config_dir = settings.getConfigDir()
        roger_env = appConfig.getRogerEnv(config_dir)
        # Remove registry key from dictionary
        del roger_env['registry']
        with self.assertRaises(ValueError):
            roger_push.main(settings, appConfig,
                            frameworkUtils, mockedHooks, args)

    def test_roger_push_with_no_environment_fails(self):
        settings = mock(Settings)
        appConfig = mock(AppConfig)
        roger_push = RogerPush()
        marathon = mock(Marathon)
        mockedHooks = mock(Hooks)
        when(mockedHooks).run_hook(any(), any(), any()).thenReturn(0)
        roger_env = self.roger_env
        config = self.config
        data = self.data
        when(marathon).put(any(), any(), any()).thenReturn("Response [200]")
        frameworkUtils = mock(FrameworkUtils)
        when(frameworkUtils).getFramework(data).thenReturn(marathon)
        when(settings).getComponentsDir().thenReturn(
            self.base_dir + "/tests/components")
        when(settings).getSecretsDir().thenReturn(
            self.base_dir + "/tests/secrets")
        when(settings).getTemplatesDir().thenReturn(
            self.base_dir + "/tests/templates")
        when(settings).getConfigDir().thenReturn(self.configs_dir)
        when(settings).getCliDir().thenReturn(self.base_dir)
        when(appConfig).getRogerEnv(any()).thenReturn(roger_env)
        when(appConfig).getConfig(any(), any()).thenReturn(config)
        when(appConfig).getAppData(any(), any(), any()).thenReturn(data)

        args = self.args
        # Set environment variable as None
        args.env = ''
        args.secrets_file = ""
        args.skip_push = True
        args.app_name = 'grafana_test_app'
        args.config_file = 'test.json'
        args.directory = self.base_dir + '/tests/testrepo'
        args.image_name = 'grafana/grafana:2.1.3'

        with self.assertRaises(ValueError):
            roger_push.main(settings, appConfig,
                            frameworkUtils, mockedHooks, args)

    def test_unresolved_jinja_variable_fails(self):

        with open(self.configs_dir + '/roger_push_unresolved_jinja.json') as config:
            config = json.load(config)
        with open(self.configs_dir + '/roger-env.json') as roger:
            roger_env = json.load(roger)
        data = config['apps']['container-vars']
        self.config = config
        self.roger_env = roger_env
        self.data = data

        settings = mock(Settings)
        appConfig = mock(AppConfig)
        roger_push = RogerPush()
        marathon = mock(Marathon)
        mockedHooks = mock(Hooks)
        when(mockedHooks).run_hook(any(), any(), any()).thenReturn(0)
        roger_env = self.roger_env
        config = self.config
        data = self.data
        frameworkUtils = mock(FrameworkUtils)
        when(frameworkUtils).getFramework(data).thenReturn(marathon)
        when(settings).getComponentsDir().thenReturn(
            self.base_dir + "/tests/components")
        when(settings).getSecretsDir().thenReturn(
            self.base_dir + "/tests/secrets")
        when(settings).getTemplatesDir().thenReturn(
            self.base_dir + "/tests/templates")
        when(settings).getConfigDir().thenReturn(self.configs_dir)
        when(settings).getCliDir().thenReturn(self.base_dir)
        when(appConfig).getRogerEnv(self.configs_dir).thenReturn(roger_env)
        when(appConfig).getConfig(self.configs_dir,
                                  "roger_push_unresolved_jinja.json").thenReturn(config)
        when(appConfig).getAppData(self.configs_dir,
                                   "roger_push_unresolved_jinja.json", "container-vars").thenReturn(data)

        args = self.args
        args.env = "dev"
        args.skip_push = False
        args.force_push = False
        args.secrets_dir = ""
        args.app_name = 'container-vars'
        args.config_file = 'roger_push_unresolved_jinja.json'
        args.directory = self.base_dir + '/tests/testrepo'
        args.image_name = 'tests/v0.1.0'

        return_code = roger_push.main(
            settings, appConfig, frameworkUtils, mockedHooks, args)
        verify(frameworkUtils, times=0).put(any(), any(), any(), any())

    def test_roger_push_calls_prepush_hook_when_present(self):
        settings = mock(Settings)
        appConfig = mock(AppConfig)
        roger_push = RogerPush()
        marathon = mock(Marathon)
        mockedHooks = mock(Hooks)
        frameworkUtils = mock(FrameworkUtils)
        roger_env = self.roger_env
        appdata = self.data
        config = self.config
        when(frameworkUtils).getFramework(any()).thenReturn(marathon)
        when(settings).getComponentsDir().thenReturn(
            self.base_dir + "/tests/components")
        when(settings).getSecretsDir().thenReturn(
            self.base_dir + "/tests/secrets")
        when(settings).getTemplatesDir().thenReturn(
            self.base_dir + "/tests/templates")
        when(settings).getConfigDir().thenReturn(self.configs_dir)
        when(settings).getCliDir().thenReturn(self.base_dir)
        when(appConfig).getRogerEnv(self.configs_dir).thenReturn(roger_env)
        when(mockedHooks).run_hook(any(), any(), any()).thenReturn(0)
        when(appConfig).getRogerEnv(any()).thenReturn(roger_env)

        appdata["hooks"] = dict([("pre_push", "some command")])
        when(appConfig).getAppData(any(), any(), any()).thenReturn(appdata)
        when(appConfig).getConfig(any(), any()).thenReturn(config)
        args = self.args
        args.config_file = 'any.json'
        args.app_name = 'any app'
        args.env = 'dev'
        args.image_name = 'tests/v0.1.0'
        args.directory = '/tmp'
        args.secrets_file = ""
        args.skip_push = True
        return_code = roger_push.main(
            settings, appConfig, frameworkUtils, mockedHooks, args)
        verify(mockedHooks).run_hook("pre_push", any(), any())

    def test_roger_push_calls_postpush_hook_when_present(self):
        settings = mock(Settings)
        appConfig = mock(AppConfig)
        roger_push = RogerPush()
        marathon = mock(Marathon)
        mockedHooks = mock(Hooks)
        frameworkUtils = mock(FrameworkUtils)
        roger_env = self.roger_env
        appdata = self.data
        config = self.config
        when(frameworkUtils).getFramework(any()).thenReturn(marathon)
        when(settings).getComponentsDir().thenReturn(
            self.base_dir + "/tests/components")
        when(settings).getSecretsDir().thenReturn(
            self.base_dir + "/tests/secrets")
        when(settings).getTemplatesDir().thenReturn(
            self.base_dir + "/tests/templates")
        when(settings).getConfigDir().thenReturn(self.configs_dir)
        when(settings).getCliDir().thenReturn(self.base_dir)
        when(appConfig).getRogerEnv(self.configs_dir).thenReturn(roger_env)
        when(mockedHooks).run_hook(any(), any(), any()).thenReturn(0)
        when(appConfig).getRogerEnv(any()).thenReturn(roger_env)

        appdata["hooks"] = dict([("post_push", "some command")])
        when(appConfig).getAppData(any(), any(), any()).thenReturn(appdata)
        when(appConfig).getConfig(any(), any()).thenReturn(config)
        args = self.args
        args.config_file = 'any.json'
        args.app_name = 'any app'
        args.env = 'dev'
        args.image_name = 'tests/v0.1.0'
        args.directory = '/tmp'
        args.secrets_file = ""
        args.skip_push = True
        return_code = roger_push.main(
            settings, appConfig, frameworkUtils, mockedHooks, args)
        verify(mockedHooks).run_hook("post_push", any(), any())

    def test_roger_push_verify_default_env_use(self):
        settings = mock(Settings)
        appConfig = mock(AppConfig)
        roger_push = RogerPush()
        marathon = mock(Marathon)
        mockedHooks = mock(Hooks)
        roger_env = self.roger_env
        config = self.config
        frameworkUtils = mock(FrameworkUtils)
        when(settings).getConfigDir().thenReturn(self.configs_dir)
        when(mockedHooks).run_hook(any(), any(), any()).thenReturn(0)
        when(appConfig).getRogerEnv(self.configs_dir).thenReturn(roger_env)
        when(appConfig).getConfig(any(), any()).thenReturn(config)

        args = self.args
        args.env = None
        args.secrets_file = ""
        args.skip_push = True
        args.app_name = 'grafana_test_app'
        args.config_file = 'test.json'

        roger_env = appConfig.getRogerEnv(self.configs_dir)
        roger_env["default"] = "test_env"

        with self.assertRaises(ValueError):
            roger_push.main(settings, appConfig,
                            frameworkUtils, mockedHooks, args)

    def test_roger_push_with_incorect_container_name(self):
        settings = mock(Settings)
        appConfig = mock(AppConfig)
        roger_push = RogerPush()
        marathon = mock(Marathon)
        mockedHooks = mock(Hooks)
        roger_env = self.roger_env
        config = self.config
        frameworkUtils = mock(FrameworkUtils)
        when(settings).getConfigDir().thenReturn(self.configs_dir)
        when(mockedHooks).run_hook(any(), any(), any()).thenReturn(0)
        when(appConfig).getRogerEnv(self.configs_dir).thenReturn(roger_env)
        when(appConfig).getConfig(any(), any()).thenReturn(config)

        args = self.args
        args.env = "dev"
        args.secrets_file = ""
        args.skip_push = True
        args.app_name = 'grafana_test_app:test'
        args.config_file = 'test.json'

        with self.assertRaises(ValueError):
            roger_push.main(settings, appConfig,frameworkUtils, mockedHooks, args)

    def test_roger_push_with_correct_container_name(self):
        settings = mock(Settings)
        appConfig = mock(AppConfig)
        roger_push = RogerPush()
        marathon = mock(Marathon)
        mockedHooks = mock(Hooks)
        roger_env = self.roger_env
        config = self.config
        frameworkUtils = mock(FrameworkUtils)
        when(settings).getConfigDir().thenReturn(self.configs_dir)
        when(mockedHooks).run_hook(any(), any(), any()).thenReturn(0)
        when(appConfig).getRogerEnv(self.configs_dir).thenReturn(roger_env)
        when(appConfig).getConfig(any(), any()).thenReturn(config)

        args = self.args
        args.env = "dev"
        args.secrets_file = ""
        args.skip_push = True
        args.app_name = 'grafana_test_app:grafana'
        args.config_file = 'test.json'

        verify(frameworkUtils, times=0).getFramework(any())

    def test_roger_push_env_from_ROGER_ENV_VAR(self):
        settings = mock(Settings)
        appConfig = mock(AppConfig)
        roger_push = RogerPush()
        marathon = mock(Marathon)
        mockedHooks = mock(Hooks)
        roger_env = self.roger_env
        config = self.config
        frameworkUtils = mock(FrameworkUtils)
        when(settings).getConfigDir().thenReturn(self.configs_dir)
        when(mockedHooks).run_hook(any(), any(), any()).thenReturn(0)
        when(appConfig).getRogerEnv(self.configs_dir).thenReturn(roger_env)
        when(appConfig).getConfig(any(), any()).thenReturn(config)

        args = self.args
        args.env = None
        args.secrets_file = ""
        args.skip_push = True
        args.app_name = 'grafana_test_app'
        args.config_file = 'test.json'

        roger_env = appConfig.getRogerEnv(self.configs_dir)
        roger_env["default"] = None
        # Setting ROGER_ENV to specific value
        os.environ["ROGER_ENV"] = "test_env"

        with self.assertRaises(ValueError):
            roger_push.main(settings, appConfig,
                            frameworkUtils, mockedHooks, args)

    def test_push_happens_with_validation_error_when_force_push_set(self):
        settings = mock(Settings)
        appConfig = mock(AppConfig)
        roger_push = RogerPush()
        marathon = mock(Marathon)
        mockedHooks = mock(Hooks)
        roger_env = self.roger_env
        config = self.config
        data = self.data
        when(marathon).put(any(), any(), any()).thenReturn("Response [200]")
        frameworkUtils = mock(FrameworkUtils)
        frameworkUtils = mock(FrameworkUtils)
        when(frameworkUtils).getFramework(data).thenReturn(marathon)
        when(settings).getComponentsDir().thenReturn(
            self.base_dir + "/tests/components")
        when(settings).getSecretsDir().thenReturn(
            self.base_dir + "/tests/secrets")
        when(settings).getTemplatesDir().thenReturn(
            self.base_dir + "/tests/templates")
        when(settings).getConfigDir().thenReturn(self.configs_dir)
        when(settings).getCliDir().thenReturn(self.base_dir)
        when(mockedHooks).run_hook(any(), any(), any()).thenReturn(0)
        when(appConfig).getRogerEnv(self.configs_dir).thenReturn(roger_env)
        when(appConfig).getConfig(any(), any()).thenReturn(config)
        when(appConfig).getAppData(any(), any(), any()).thenReturn(data)

        args = self.args
        args.env = "dev"
        args.secrets_file = ""
        args.skip_push = False
        args.force_push = True
        args.app_name = 'grafana_test_app'
        args.config_file = 'test.json'
        args.directory = self.base_dir + '/tests/testrepo'
        args.image_name = 'grafana/grafana:2.1.3'
        roger_push.main(settings, appConfig, frameworkUtils, mockedHooks, args)

    def test_roger_push_skip_push_set(self):
        settings = mock(Settings)
        appConfig = mock(AppConfig)
        roger_push = RogerPush()
        marathon = mock(Marathon)
        mockedHooks = mock(Hooks)
        roger_env = self.roger_env
        config = self.config
        data = self.data
        when(marathon).put(any(), any(), any()).thenReturn("Response [200]")
        frameworkUtils = mock(FrameworkUtils)
        when(frameworkUtils).getFramework(data).thenReturn(marathon)
        when(settings).getComponentsDir().thenReturn(
            self.base_dir + "/tests/components")
        when(settings).getSecretsDir().thenReturn(
            self.base_dir + "/tests/secrets")
        when(settings).getTemplatesDir().thenReturn(
            self.base_dir + "/tests/templates")
        when(settings).getConfigDir().thenReturn(self.configs_dir)
        when(settings).getCliDir().thenReturn(self.base_dir)
        when(mockedHooks).run_hook(any(), any(), any()).thenReturn(0)
        when(appConfig).getRogerEnv(self.configs_dir).thenReturn(roger_env)
        when(appConfig).getConfig(any(), any()).thenReturn(config)
        when(appConfig).getAppData(any(), any(), any()).thenReturn(data)

        args = self.args
        args.env = "dev"
        args.secrets_file = ""
        args.skip_push = True
        args.app_name = 'grafana_test_app'
        args.config_file = 'test.json'
        args.directory = self.base_dir + '/tests/testrepo'
        args.image_name = 'grafana/grafana:2.1.3'

        return_code = roger_push.main(
            settings, appConfig, frameworkUtils, mockedHooks, args)
        verify(frameworkUtils, times=0).runDeploymentChecks(any(), any())

    def test_push_fails_with_validation_error(self):
        settings = mock(Settings)
        appConfig = mock(AppConfig)
        roger_push = RogerPush()
        marathon = mock(Marathon)
        mockedHooks = mock(Hooks)
        roger_env = self.roger_env
        config = self.config
        data = self.data
        frameworkUtils = mock(FrameworkUtils)
        when(frameworkUtils).getFramework(data).thenReturn(marathon)
        when(settings).getComponentsDir().thenReturn(
            self.base_dir + "/tests/components")
        when(settings).getSecretsDir().thenReturn(
            self.base_dir + "/tests/secrets")
        when(settings).getTemplatesDir().thenReturn(
            self.base_dir + "/tests/templates")
        when(settings).getConfigDir().thenReturn(self.configs_dir)
        when(settings).getCliDir().thenReturn(self.base_dir)
        when(mockedHooks).run_hook(any(), any(), any()).thenReturn(0)
        when(appConfig).getRogerEnv(self.configs_dir).thenReturn(roger_env)
        when(appConfig).getConfig(any(), any()).thenReturn(config)
        when(appConfig).getAppData(any(), any(), any()).thenReturn(data)

        args = self.args
        args.env = "dev"
        args.secrets_file = ""
        args.skip_push = False
        args.force_push = False
        args.app_name = 'grafana_test_app'
        args.config_file = 'test.json'
        args.directory = self.base_dir + '/tests/testrepo'
        args.image_name = 'grafana/grafana:2.1.3'
        return_code = roger_push.main(
            settings, appConfig, frameworkUtils, mockedHooks, args)
        verify(frameworkUtils, times=0).put(any(), any(), any(), any())

    def test_roger_push_secrets_replaced(self):
        settings = mock(Settings)
        appConfig = mock(AppConfig)
        roger_push = RogerPush()
        marathon = mock(Marathon)
        mockedHooks = mock(Hooks)
        roger_env = self.roger_env
        config = self.config
        data = self.data
        when(marathon).put(any(), any(), any()).thenReturn("Response [200]")
        frameworkUtils = mock(FrameworkUtils)
        when(frameworkUtils).getFramework(data).thenReturn(marathon)
        when(settings).getComponentsDir().thenReturn(
            self.base_dir + "/tests/components")
        when(settings).getSecretsDir().thenReturn(
            self.base_dir + "/tests/secrets")
        when(settings).getTemplatesDir().thenReturn(
            self.base_dir + "/tests/templates")
        when(settings).getConfigDir().thenReturn(self.configs_dir)
        when(settings).getCliDir().thenReturn(self.base_dir)
        when(appConfig).getRogerEnv(any()).thenReturn(roger_env)
        when(appConfig).getConfig(any(), any()).thenReturn(config)
        when(appConfig).getAppData(any(), any(), any()).thenReturn(data)
        when(mockedHooks).run_hook(any(), any(), any()).thenReturn(0)

        args = self.args
        args.env = "dev"
        args.secrets_file = ""
        args.skip_push = True
        args.app_name = 'grafana_test_app'
        args.config_file = 'test.json'
        args.directory = self.base_dir + '/tests/testrepo'
        args.image_name = 'grafana/grafana:2.1.3'
        exit_code = roger_push.main(
            settings, appConfig, frameworkUtils, mockedHooks, args)
        file_path = ("{0}/{1}/{2}".format(self.components_dir,
                                          args.env, args.config_file))
        assert (os.path.isfile(file_path) is not True)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
