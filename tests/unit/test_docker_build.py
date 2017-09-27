#!/usr/bin/python

from __future__ import print_function
import unittest
import argparse
import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(os.path.realpath(__file__)), os.pardir, "cli")))
from cli.appconfig import AppConfig
from cli.settings import Settings
from mockito import mock, when, verify
from mockito.matchers import any
from cli.dockerutils import DockerUtils
from cli.docker_build import Docker

# Test basic functionalities of docker-build


class TestBuild(unittest.TestCase):

    def setUp(self):
        self.settingObj = Settings()
        self.base_dir = self.settingObj.getCliDir()
        self.configs_dir = self.base_dir + "/tests/configs"
        self.components_dir = self.base_dir + '/tests/components/dev'
        self.configs_dir = self.base_dir + "/tests/configs"
        with open(self.configs_dir + '/app.json') as config:
            config = json.load(config)
        self.config = config

    def test_docker_build(self):
        raised_exception = False
        try:
            appObj = mock(AppConfig)
            dockerUtilsObj = mock(DockerUtils)
            dockerObj = Docker()
            when(appObj).getRepoName(any()).thenReturn('roger')
            when(dockerUtilsObj).docker_build(any(), any()).thenReturn(True)
            directory = self.base_dir + '/tests/testrepo'
            config = self.config
            repo = config['repo']
            projects = 'none'
            path = ''
            image_tag = 'test_image_tag'
            build_filename = ''
            verbose_mode = False
            dockerObj.docker_build(dockerUtilsObj, appObj,
                                   directory, repo, projects, path, image_tag, verbose_mode, build_filename)
        except (Exception) as e:
            print("Build error is: ")
            print(e)
            raised_exception = True
        self.assertFalse(raised_exception)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
