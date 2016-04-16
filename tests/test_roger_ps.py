#!/usr/bin/python

from __future__ import print_function
import unittest
import os
import sys
import argparse
sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(os.path.realpath(__file__)), os.pardir, "cli")))
from roger_ps import RogerPS
from haproxyparser import HAProxyParser
from marathon import Marathon
from mockito import mock, when


class TestRogerPS(unittest.TestCase):

    def setUp(self):
        self.rogerps = RogerPS()
        parser = argparse.ArgumentParser(description='Args for test')
        parser.add_argument('-e', '--environment', metavar='env',
                            help="Environment to deploy. example: 'dev' or 'stage'")
        parser.add_argument(
            '-v', '--verbose', help="provides instance details for each app.", action="store_true")
        self.parser = parser
        self.args = parser
        roger_env = {}
        environment = {}
        test = {}
        test['host'] = "http://testhost"
        environment['test'] = test
        roger_env['environments'] = environment
        self.roger_env = roger_env
        framework = mock(Marathon)
        app_envs = {}
        instance_details = {}
        app_envs['app1'] = {"HTTP_PORT": "PORT0", "ENVKEY1": "value1"}
        app_envs['app2'] = {"ENVKEY1": "value1"}
        instance_details[
            'app1-123'] = ("app1", "host1", ['3000', '3001'], "2016-03-18T20:48:13.732Z")
        instance_details[
            'app2-efg'] = ("app2", "host2", ['9000'], "2016-04-18T20:48:13.732Z")
        when(framework).getAppEnvDetails(
            self.roger_env, "test").thenReturn(app_envs)
        when(framework).getInstanceDetails(
            self.roger_env, "test").thenReturn(instance_details)
        self.framework = framework
        haproxyparser = mock(HAProxyParser)
        path_beg_values = {}
        path_beg_values['/test/app1'] = "app1"
        backend_services_tcp_ports = {}
        backend_services_tcp_ports['9001'] = "app2"
        when(haproxyparser).get_backend_tcp_ports(
        ).thenReturn(backend_services_tcp_ports)
        when(haproxyparser).parseConfig("test").thenReturn(
            "acl ::test::app-aclrule path_beg -i /test/app\nacl ::test::links-aclrule path_beg -i /test/links")
        when(haproxyparser).get_path_begin_values().thenReturn(path_beg_values)
        self.haproxyparser = haproxyparser

    def test_get_marathon_details_correctly_parses_tasks_and_haproxy_details_with_no_verbose(self):
        args = self.args
        args.verbose = False
        app_details = self.rogerps.get_app_details(
            self.framework, self.haproxyparser, "test", args, self.roger_env)
        assert app_details['apps']['app1'][
            'http_url'] == "http://testhost/test/app1"
        assert app_details['apps']['app2']['http_url'] == "-"
        assert app_details['apps']['app1']['tcp_port_list'] == "-"
        assert app_details['apps']['app2']['tcp_port_list'] == "9001"
        assert ('tasks' in app_details['apps']['app1']) is False
        assert ('tasks' in app_details['apps']['app2']) is False

    def test_get_marathon_details_correctly_parses_tasks_and_haproxy_details_with_verbose(self):
        args = self.args
        args.verbose = True
        app_details = self.rogerps.get_app_details(
            self.framework, self.haproxyparser, "test", args, self.roger_env)
        assert ('tasks' in app_details['apps']['app1']) is True
        assert ('tasks' in app_details['apps']['app2']) is True
        assert app_details['apps']['app1']['tasks'][
            'app1-123']['hostname'] == "host1"

    def test_get_instance_details(self):
        instance_details = self.rogerps.get_instance_details(
            self.framework, self.roger_env, "test")
        assert instance_details.keys() == ['app1-123', 'app2-efg']
        app1_data = instance_details['app1-123']
        app2_data = instance_details['app2-efg']
        assert app1_data[1] == "host1"
        assert app1_data[2] == ['3000', '3001']
        assert app2_data[0] == "app2"
        assert app2_data[2] == ['9000']
        assert app2_data[3] == "2016-04-18T20:48:13.732Z"

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
