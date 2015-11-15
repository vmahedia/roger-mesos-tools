#!/usr/bin/python

from __future__ import print_function
import unittest
import os
import sys
import imp
roger_git_pull = imp.load_source('roger_git_pull', '/vagrant/bin/roger-git-pull')

#Test basic functionalities of roger-git-pull script
class TestGitPull(unittest.TestCase):

  def setUp(self):
    pass

  def tearDown(self):
    pass

if __name__ == '__main__':
  unittest.main()
