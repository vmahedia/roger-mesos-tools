#!/usr/bin/python

from __future__ import print_function
import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(os.path.realpath(__file__)), os.pardir, "cli")))
from utils import Utils
from appconfig import AppConfig

# Test basic functionalities of Settings class


class TestUtils(unittest.TestCase):

    def setUp(self):
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

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
