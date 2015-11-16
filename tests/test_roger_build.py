#!/usr/bin/python

from __future__ import print_function
import unittest
import os
import sys
sys.path.append('/vagrant/bin')
import imp
roger_build = imp.load_source('roger_build', '/vagrant/bin/roger-build')

#Test basic functionalities of roger-build script
class TestBuild(unittest.TestCase):

  def setUp(self):
    pass

  def tearDown(self):
    pass

if __name__ == '__main__':
  unittest.main()
