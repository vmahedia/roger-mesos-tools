i#!/usr/bin/python

from __future__ import print_function
import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, "cli")))
from marathonvalidator import MarathonValidator

#Test basic functionalities of MarathonValidator class
class TestMarathonValidator(unittest.TestCase):

  def setUp(self):
    self.marathonvalidator = MarathonValidator()

  def test_check_http_prefix(self)

  def tearDown(self):
    pass


if __name__ == '__main__':
  unittest.main()
