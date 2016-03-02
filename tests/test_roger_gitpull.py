#!/usr/bin/python

from __future__ import print_function
import unittest
import os
import json
import shutil
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, "cli")))
import roger_gitpull
from settings import Settings

#Test basic functionalities of roger-git-pull script
class TestGitPull(unittest.TestCase):

  def setUp(self):
    self.settingObj = Settings()
    self.base_dir = self.settingObj.getCliDir()
    self.configs_dir = self.base_dir+"/tests/configs"
    self.work_dir = self.base_dir+"/tests/work_dir"
    pass

  def test_rogerGitPull(self):
    set_config_dir = ''
    if "ROGER_CONFIG_DIR" in os.environ:
      set_config_dir = os.environ.get('ROGER_CONFIG_DIR')
    os.environ["ROGER_CONFIG_DIR"] = self.configs_dir
    config_file = "app.json"
    work_dir = self.work_dir
    os.system("roger gitpull test_app {} {}".format(work_dir, config_file))
    with open(self.configs_dir+'/{}'.format(config_file)) as config:
      config = json.load(config)
    repo = config['repo']
    exists = os.path.exists(work_dir)
    assert exists == True
    exists = os.path.exists("{}/{}".format(work_dir, repo))
    assert exists == True
    exists = os.path.exists("{}/{}/ansible".format(work_dir, repo))
    assert exists == True
    shutil.rmtree(work_dir)
    if set_config_dir.strip() != '':
      os.environ["ROGER_CONFIG_DIR"] = "{}".format(set_config_dir)

  def tearDown(self):
    pass

if __name__ == '__main__':
  unittest.main()
