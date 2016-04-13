#!/usr/bin/python

from __future__ import print_function
import unittest
import os
import sys
import argparse
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, "cli")))
from roger_ps import RogerPS
from haproxyparser import HAProxyParser
from mockito import mock, when

#Test basic functionalities of MarathonValidator class
class TestRogerPS(unittest.TestCase):

    def setUp(self):
        self.rogerps = RogerPS()
        parser = argparse.ArgumentParser(description='Args for test')
        parser.add_argument('-e', '--environment', metavar='env', help="Environment to deploy. example: 'dev' or 'stage'")
        parser.add_argument('-v','--verbose', help="provides instance details for each app.",  action="store_true")
        self.parser = parser
        self.args = parser
        tasks = []
        task1 = {}
        task1["appId"] = "app1"
        task1["startedAt"] = "2016-03-18T20:48:13.732Z"
        task1["host"] = "host1"
        task1["ports"] = ['3000','3001']
        task1["id"] = "app1-123"
        task2 = {}
        task2["appId"] = "app2"
        task2["startedAt"] = "2016-04-18T20:48:13.732Z"
        task2["host"] = "host2"
        task2["ports"] = ['9000']
        task2["id"] = "app2-efg"
        tasks.append(task1)
        tasks.append(task2)
        self.tasks = tasks

    def test_get_marathon_details(self):
        haproxyparser = mock(HAProxyParser)
        path_beg_values = {}
        path_beg_values['/test/app1'] = "app1"
        backend_services_tcp_ports = {}
        backend_services_tcp_ports['9001'] = "app2"
        when(haproxyparser).get_backend_tcp_ports().thenReturn(backend_services_tcp_ports)
        when(haproxyparser).parseConfig("test").thenReturn("acl ::test::app-aclrule path_beg -i /test/app\nacl ::test::links-aclrule path_beg -i /test/links")
        when(haproxyparser).get_path_begin_values().thenReturn(path_beg_values)
        args = self.args
        args.verbose = False
        marathon_details = self.rogerps.get_marathon_details(self.tasks, haproxyparser, "test", args)
        assert marathon_details['apps']['app1']['http_prefix'] == "/test/app1"
        assert marathon_details['apps']['app2']['http_prefix'] == ""
        assert marathon_details['apps']['app1']['tcp_port_list'] == []
        assert marathon_details['apps']['app2']['tcp_port_list'] == "9001"
        assert ('tasks' in marathon_details['apps']['app1']) == False
        assert ('tasks' in marathon_details['apps']['app2']) == False
        args.verbose = True
        marathon_details = self.rogerps.get_marathon_details(self.tasks, haproxyparser, "test", args)
        assert ('tasks' in marathon_details['apps']['app1']) == True
        assert ('tasks' in marathon_details['apps']['app2']) == True
        assert marathon_details['apps']['app1']['tasks']['app1-123']['hostname'] == "host1"


    def test_get_instance_details(self):
        instance_details = self.rogerps.get_instance_details(self.tasks) 
        assert instance_details.keys() == ['app1-123', 'app2-efg']
        app1_data = instance_details['app1-123']
        app2_data = instance_details['app2-efg']
        assert app1_data[1] == "host1"
        assert app1_data[2] == ['3000','3001']
        assert app2_data[0] == "app2"
        assert app2_data[2] == ['9000']
        assert app2_data[3] == "2016-04-18T20:48:13.732Z"

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
