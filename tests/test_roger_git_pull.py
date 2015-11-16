#!/usr/bin/python

from __future__ import print_function
import unittest
import os
import json
import shutil
import sys
sys.path.append('/vagrant/bin')
import imp
roger_git_pull = imp.load_source('roger_git_pull', '/vagrant/bin/roger-git-pull')

#Test basic functionalities of roger-git-pull script
class TestGitPull(unittest.TestCase):

  def setUp(self):
    pass

  def test_rogerGitPull(self):
    set_config_dir = ''
    if "ROGER_CONFIG_DIR" in os.environ:
      set_config_dir = os.environ.get('ROGER_CONFIG_DIR')
    os.environ["ROGER_CONFIG_DIR"] = "/vagrant/tests/configs"
    config_file = "app.json"
    work_dir = "/vagrant/tests/work_dir"
    os.system("roger-git-pull test_app {} {}".format(work_dir, config_file))
    with open('/vagrant/tests/configs/{}'.format(config_file)) as config:
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
