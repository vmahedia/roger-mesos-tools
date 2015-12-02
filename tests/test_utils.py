#!/usr/bin/python

from __future__ import print_function
import unittest
import os
import sys
sys.path.append('/vagrant/cli')
from utils import Utils
from appConfig import AppConfig

#Test basic functionalities of Settings class
class TestUtils(unittest.TestCase):

  def setUp(self):
    self.utils = Utils()
    self.appConfig = AppConfig()

  def test_extractFullShaAndVersion(self):
    assert self.utils.extractFullShaAndVersion("moz-content-kairos-7da406eb9e8937875e0548ae1149/v0.46") == "7da406eb9e8937875e0548ae1149/v0.46"
    assert self.utils.extractFullShaAndVersion("") == ""
    assert self.utils.extractFullShaAndVersion("bdsbddadhhd") == ""

  def test_extractShaFromImage(self):
    assert self.utils.extractShaFromImage("moz-content-kairos-7da406eb9e8937875e0548ae1149/v0.46") == "7da406eb9e8937875e0548ae1149"
    assert self.utils.extractShaFromImage("") == ""
    assert self.utils.extractShaFromImage("bdsbddadhhd") == ""

  '''
  def test_getFramework(self):
    data = self.appConfig.getAppData("/vagrant/tests/configs", "app.json", "test_app")
    assert self.utils.getFramework(data) == "marathon"
    data = self.appConfig.getAppData("/vagrant/tests/configs", "app.json", "test_app1")
    assert self.utils.getFramework(data) == "chronos"
    data = self.appConfig.getAppData("/vagrant/tests/configs", "app.json", "appdoesnotexist")
    assert self.utils.getFramework(data) == "marathon"

  def test_setgetFramework(self):
    self.utils.setFramework("marathon")
    data = self.appConfig.getAppData("/vagrant/tests/configs", "app.json", "test_app1")
    assert self.utils.getFramework(data) == "marathon"
    self.utils.setFramework("testframework")
    assert self.utils.getFramework(data) == "testframework"
  '''

  def tearDown(self):
    pass

if __name__ == '__main__':
  unittest.main()
