#!/usr/bin/python

from __future__ import print_function
import unittest
import argparse
import os
import sys
sys.path.append('/vagrant/bin')
import imp
roger_deploy = imp.load_source('roger_deploy', '/vagrant/bin/roger-deploy')

#Test basic functionalities of roger-deploy script
class TestDeploy(unittest.TestCase):

  def setUp(self):
    parser = argparse.ArgumentParser(description='Args for test')
    #parser.add_argument('command', metavar='command', help="Command to run")
    self.parser = parser

  def test_splitVersion(self):
    assert roger_deploy.splitVersion("0.1.0") == (0,1,0)
    assert roger_deploy.splitVersion("2.0013") == (2,13,0)
    
  def test_incrementVersion(self):
    git_sha = "dwqjdqgwd7y12edq21"
    image_version_list = ['0.001','0.2.034','1.1.2','1.002.1']
    parser = self.parser
    parser.add_argument('-M', '--incr-major', action="store_true",
    help="Increment major in version. Defaults to false.'")
    parser.add_argument('-p', '--incr-patch', action="store_true",
    help="Increment patch in version. Defaults to false.'")
    args = parser.parse_args()
    assert roger_deploy.incrementVersion(git_sha, image_version_list, args) == 'dwqjdqgwd7y12edq21/v1.3.0'
    args.incr_patch = True
    assert roger_deploy.incrementVersion(git_sha, image_version_list, args) == 'dwqjdqgwd7y12edq21/v1.2.2'
    args.incr_major = True
    assert roger_deploy.incrementVersion(git_sha, image_version_list, args) == 'dwqjdqgwd7y12edq21/v2.0.0'

  def test_tempDirCheck(self):
    work_dir = "./test_dir"
    roger_deploy.removeDirTree(work_dir)
    exists = os.path.exists(os.path.abspath(work_dir))
    assert exists == False
    os.makedirs(work_dir)
    exists = os.path.exists(os.path.abspath(work_dir))
    assert exists == True
    roger_deploy.removeDirTree(work_dir)
    exists = os.path.exists(os.path.abspath(work_dir))
    assert exists == False

  def tearDown(self):
    pass  

if __name__ == '__main__':
  unittest.main()
