#!/usr/bin/python

from __future__ import print_function
import unittest
import os
import json
import sys
import shutil
sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(os.path.realpath(__file__)), os.pardir, "cli")))
from cli.settings import Settings
from cli.gitutils import GitUtils

import pytest

# Test basic functionalities of roger-init script


@pytest.mark.skip
class TestInit(unittest.TestCase):

    def setUp(self):
        self.gitObj = GitUtils()
        self.settingObj = Settings()
        self.base_dir = self.settingObj.getCliDir()
        self.configs_dir = self.base_dir + "/tests/configs"
        self.work_dir = self.base_dir + "/tests/work_dir"
        self.branch = "master"

    def test_gitPull(self):
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
        with open(self.configs_dir + '/{}'.format(config_file)) as config:
            config = json.load(config)
        repo = config['repo']
        return_code = self.gitObj.gitClone(repo, branch)
        assert return_code == 0
        exists = os.path.exists(work_dir)
        assert exists is True
        os.chdir("{}/{}".format(work_dir, repo))
        return_code = self.gitObj.gitPull(self.branch)
        assert return_code == 0
        assert exists is True
        exists = os.path.exists("{}/{}".format(work_dir, repo))
        assert exists is True
        exists = os.path.exists("{}/{}/ansible".format(work_dir, repo))
        assert exists is True
        shutil.rmtree(work_dir)
        pass

    def test_gitShallowClone(self):
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
        with open(self.configs_dir + '/{}'.format(config_file)) as config:
            config = json.load(config)
        repo = config['repo']
        return_code = self.gitObj.gitShallowClone(repo, branch)
        assert return_code == 0
        exists = os.path.exists(work_dir)
        assert exists is True
        exists = os.path.exists("{}/{}".format(work_dir, repo))
        assert exists is True
        exists = os.path.exists("{}/{}/ansible".format(work_dir, repo))
        assert exists is True
        shutil.rmtree(work_dir)

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
        with open(self.configs_dir + '/{}'.format(config_file)) as config:
            config = json.load(config)
        repo = config['repo']
        return_code = self.gitObj.gitClone(repo, branch)
        assert return_code == 0
        exists = os.path.exists(work_dir)
        assert exists is True
        exists = os.path.exists("{}/{}".format(work_dir, repo))
        assert exists is True
        exists = os.path.exists("{}/{}/ansible".format(work_dir, repo))
        assert exists is True
        shutil.rmtree(work_dir)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
