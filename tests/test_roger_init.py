#!/usr/bin/python

from __future__ import print_function
import unittest
import os
import sys
import imp
roger_init = imp.load_source('roger_init', '/vagrant/bin/roger-init')

#Test basic functionalities of roger-init script
class TestInit(unittest.TestCase):

  def setUp(self):
    pass

  def tearDown(self):
    pass

if __name__ == '__main__':
    unittest.main()
