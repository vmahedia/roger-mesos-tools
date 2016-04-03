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
    when(haproxyparser).parseConfig("test").thenReturn("acl ::test::app-aclrule path_beg -i /test/app\nacl ::test::links-aclrule path_beg -i /test/links")
    when(haproxyparser).get_path_begin_values().thenReturn(path_beg_values)
    assert self.marathonvalidator.check_path_begin_value(haproxyparser, "/test", "/test/app") == True
    #Negative test case
    assert self.marathonvalidator.check_path_begin_value(haproxyparser, "/test/app", "/test") == False
    assert self.marathonvalidator.check_path_begin_value(haproxyparser, "", "/test/app") == True
    assert self.marathonvalidator.check_path_begin_value(haproxyparser, "/test/links", "/test/links") == True
    assert self.marathonvalidator.check_path_begin_value(haproxyparser, "/constance", "/test/app") == True
    #Negative test case
    assert self.marathonvalidator.check_path_begin_value(haproxyparser, "/service2", "/service2") == False
    assert self.marathonvalidator.check_path_begin_value(haproxyparser, "/service2", "/app3/service2") == True
    assert self.marathonvalidator.check_path_begin_value(haproxyparser, "/app/service2", "/app3/service") == True
    assert self.marathonvalidator.check_path_begin_value(haproxyparser, "/app/service2", "/test/app2/service") == True
    assert self.marathonvalidator.check_path_begin_value(haproxyparser, "/service", "/test/app2/service") == True

  def test_check_tcp_port(self):
    haproxyparser = mock(HAProxyParser)
    backend_services_tcp_ports = {}
    backend_services_tcp_ports['3000'] = "/test/app"
    backend_services_tcp_ports['30001'] = "/test/app"
    backend_services_tcp_ports['9004'] = "/app1/links"
    backend_services_tcp_ports['9090'] = "/test/app2/service"
    when(haproxyparser).parseConfig("test").thenReturn("listen ::test::app-cluster-tcp-3000 :3000\nlisten ::test::app-cluster-tcp-3001 :3001")
    when(haproxyparser).get_backend_tcp_ports().thenReturn(backend_services_tcp_ports)
    assert self.marathonvalidator.check_tcp_port(haproxyparser, [ "3000", "3001" ], "/test/app") == True
    assert self.marathonvalidator.check_tcp_port(haproxyparser, [ "3000" ], "/test/app") == True
    assert self.marathonvalidator.check_tcp_port(haproxyparser, [ "3000", "3001", "3002" ], "/test/app") == True
    assert self.marathonvalidator.check_tcp_port(haproxyparser, [ "9090", "9000" ], "/test/app2/service") == True
    #Negative test cases
    assert self.marathonvalidator.check_tcp_port(haproxyparser, [ "3000", "9000" ], "/test/app1") == False
    assert self.marathonvalidator.check_tcp_port(haproxyparser, [ "9090", "9000" ], "/test/app1/service") == False

  def tearDown(self):
    pass

if __name__ == '__main__':
  unittest.main()
