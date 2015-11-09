#!/usr/bin/python

from __future__ import print_function
import unittest
import os
import sys
import imp
roger_deploy = imp.load_source('roger_deploy', '/vagrant/bin/roger-deploy')

#Test basic functionalities of roger-deploy script
class TestJournal(unittest.TestCase):

  def setUp(self):
    pass

  def test_splitVersion(self):
    assert roger_deploy.splitVersion("0.1.0") == (0,1,0)
    assert roger_deploy.splitVersion("2.0013") == (2,13,0)

  def tearDown(self):
    pass  

if __name__ == '__main__':
    unittest.main()
