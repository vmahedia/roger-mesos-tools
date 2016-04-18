#!/usr/bin/python

from __future__ import print_function
import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(os.path.realpath(__file__)), os.pardir, "cli")))
from marathon import Marathon
from mockito import mock, when

# Test basic functionalities of MarathonValidator class


class TestMarathon(unittest.TestCase):

    def setUp(self):
        self.marathon = Marathon()

    def test_validateGroupDetails(self):
        group_details = {}
        message_list = []
        group_details['/test/app1'] = ('/http_prefix1', ['3000', '3001'])
        group_details['/test/app2'] = ('/http_prefix2', ['9000', '9001'])
        valid = self.marathon.validateGroupDetails(group_details, message_list)
        assert valid is True
        assert len(message_list) == 0
        message_list = []
        group_details['/test/app3'] = ('/http_prefix3', ['8000', '9001'])
        valid = self.marathon.validateGroupDetails(group_details, message_list)
        assert valid is False
        assert len(message_list) == 1
        message_list = []
        group_details['/test/app4'] = ('/http_prefix3', ['7000', '7001'])
        valid = self.marathon.validateGroupDetails(group_details, message_list)
        assert valid is False
        assert len(message_list) == 2
        for message in message_list:
            print(message)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
