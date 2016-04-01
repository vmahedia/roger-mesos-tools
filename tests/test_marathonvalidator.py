#!/usr/bin/python

from __future__ import print_function
import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, "cli")))
from marathonvalidator import MarathonValidator
from haproxyparser import HAProxyParser
from mockito import mock, when

#Test basic functionalities of MarathonValidator class
class TestMarathonValidator(unittest.TestCase):

  def setUp(self):
    self.marathonvalidator = MarathonValidator()

  def test_check_path_begin(self):
    haproxyparser = mock(HAProxyParser)
    path_beg_values = {}
    path_beg_values['/test/app'] = "/test/app"
    path_beg_values['/test/links'] = "/test/links"
    path_beg_values['/app1/links'] = "/app1/links"
    path_beg_values['/app2/service'] = "/test/app2/service"
    path_beg_values['/service2'] = "/app3/service2"
    when(haproxyparser).parseConfig("dev").thenReturn("acl ::test::app-aclrule path_beg -i /test/app\n acl ::test::links-aclrule path_beg -i /test/links")
    when(haproxyparser).get_path_begin_values().thenReturn(path_beg_values)
    assert self.marathonvalidator.check_path_begin_value(haproxyparser, "dev", "/test", "/test/app") == True
    #Negative test case
    assert self.marathonvalidator.check_path_begin_value(haproxyparser, "dev", "/test/app", "/test") == False
    assert self.marathonvalidator.check_path_begin_value(haproxyparser, "dev", "", "/test/app") == True
    assert self.marathonvalidator.check_path_begin_value(haproxyparser, "dev", "/test/links", "/test/links") == True
    assert self.marathonvalidator.check_path_begin_value(haproxyparser, "dev", "/constance", "/test/app") == True
    #Negative test case
    assert self.marathonvalidator.check_path_begin_value(haproxyparser, "dev", "/service2", "/service2") == False
    assert self.marathonvalidator.check_path_begin_value(haproxyparser, "dev", "/service2", "/app3/service2") == True
    assert self.marathonvalidator.check_path_begin_value(haproxyparser, "dev", "/app/service2", "/app3/service") == True
    assert self.marathonvalidator.check_path_begin_value(haproxyparser, "dev", "/app/service2", "/test/app2/service") == True
    assert self.marathonvalidator.check_path_begin_value(haproxyparser, "dev", "/service", "/test/app2/service") == True

  def tearDown(self):
    pass

if __name__ == '__main__':
  unittest.main()
