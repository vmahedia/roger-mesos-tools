#!/usr/bin/python


from __future__ import print_function
import tests.helper
import unittest
import os
import sys
import argparse
sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(os.path.realpath(__file__)), os.pardir, "cli")))
from cli.utils import Utils
from cli.appconfig import AppConfig
from mockito import mock, Mock, when


class TestUtils(unittest.TestCase):

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
        self.utils = Utils()
        self.appConfig = AppConfig()

    def test_extractFullShaAndVersion(self):
        assert self.utils.extractFullShaAndVersion(
            "testproject-testapp-26363727sha232/v0.46") == "26363727sha232/v0.46"
        assert self.utils.extractFullShaAndVersion("") == ""
        assert self.utils.extractFullShaAndVersion("bdsbddadhhd") == ""

    def test_extractShaFromImage(self):
        assert self.utils.extractShaFromImage(
            "testproject-testapp-779824982sha123/v0.46") == "779824982sha123"
        assert self.utils.extractShaFromImage("") == ""
        assert self.utils.extractShaFromImage("bdsbddadhhd") == ""


if __name__ == '__main__':
    unittest.main()
