# -*- encoding: utf-8 -*-

"""
Unit test for roger_promote.py

"""

import tests.helper

import unittest
import os


from mockito import mock, Mock, when


from cli.roger_promote import RogerPromote
from cli.appconfig import AppConfig
from cli.settings import Settings


class TestRogerPromote(unittest.TestCase):
    def setUp(self):
        self.settings = mock(Settings)


    def test_config_dir(self):
        when(self.settings).getConfigDir().thenReturn('/vag')
