#!/usr/bin/python

from __future__ import print_function
import unittest
import os
import json
import sys
import shutil
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, "cli")))
from settings import Settings
from gitutils  import GitUtils

#Test basic functionalities of roger-init script
class TestInit(unittest.TestCase):

  def setUp(self):
    self.gitObj = GitUtils()
    self.settingObj = Settings()
    self.base_dir = self.settingObj.getCliDir()
    self.configs_dir = self.base_dir+"/tests/configs"
    self.work_dir = self.base_dir+"/tests/work_dir"
    self.branch = "master"
    pass

  def test_gitPull(self):
    pass

  def test_gitClone(self):
    config_file = "app.json"
    work_dir = self.work_dir
    branch = self.branch

    if not os.path.exists(self.work_dir):
      try:
          os.makedirs(self.work_dir)
      except OSError as exception:
          if exception.errno != errno.EEXIST:
              raise
    os.chdir(self.work_dir)
    with open(self.configs_dir+'/{}'.format(config_file)) as config:
      config = json.load(config)
    repo = config['repo']
    self.gitObj.gitClone(branch,repo)
    exists = os.path.exists(work_dir)
    assert exists == True
    exists = os.path.exists("{}/{}".format(work_dir, repo))
    assert exists == True
    exists = os.path.exists("{}/{}/ansible".format(work_dir, repo))
    assert exists == True
    shutil.rmtree(work_dir)
    pass


  def tearDown(self):
    pass

if __name__ == '__main__':
  unittest.main()
