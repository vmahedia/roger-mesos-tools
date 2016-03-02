#!/usr/bin/python

from __future__ import print_function
import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, "cli")))
import roger_build

#Test basic functionalities of roger-build script
class TestBuild(unittest.TestCase):

  def setUp(self):
    pass

  def tearDown(self):
    pass

if __name__ == '__main__':
  unittest.main()
