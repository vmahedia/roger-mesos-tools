#!/usr/bin/python

from __future__ import print_function
import argparse
import json
import os
import sys
from cli.settings import Settings
from cli.appconfig import AppConfig
from cli.gitutils import GitUtils
from cli.hooks import Hooks
import errno

import contextlib


@contextlib.contextmanager
def chdir(dirname):
    '''Withable chdir function that restores directory'''
    curdir = os.getcwd()
    try:
        os.chdir(dirname)
        yield
    finally:
        os.chdir(curdir)


def describe():
    return 'pulls code from the application git repository (clones the repository).'


class RogerGitPull(object):

    def parse_args(self):
        self.parser = argparse.ArgumentParser(
            prog='roger gitpull', description=describe())
        self.parser.add_argument('app_name', metavar='app_name',
                                 help="application for which code is to be pulled. Example: 'agora' or 'grafana'")
        self.parser.add_argument('directory', metavar='directory',
                                 help="working directory. The repo has its own directory it this. Example: '/home/vagrant/work_dir'")
        self.parser.add_argument('-b', '--branch', metavar='branch',
                                 help="git branch to pull code from. Example: 'production' or 'master'. Defaults to master.")
        self.parser.add_argument('config_file', metavar='config_file',
                                 help="configuration file to use. Example: 'content.json' or 'kwe.json'")
        return self.parser

    def main(self, settings, appConfig, gitObject, hooksObj, args):
        settingObj = settings
        appObj = appConfig
        gitObj = gitObject
        config_dir = settingObj.getConfigDir()
        config = appObj.getConfig(config_dir, args.config_file)

        common_repo = config.get('repo', '')
        data = appObj.getAppData(config_dir, args.config_file, args.app_name)
        if not data:
            raise ValueError('Application with name [{}] or data for it not found at {}/{}.'.format(
                args.app_name, config_dir, args.config_file))
        repo = ''
        if common_repo != '':
            repo = data.get('repo', common_repo)
        else:
            repo = data.get('repo', args.app_name)

        branch = "master"  # master by default
        if args.branch is not None:
            branch = args.branch

        if not os.path.exists(args.directory):
            try:
                os.makedirs(args.directory)
            except OSError as exception:
                if exception.errno != errno.EEXIST:
                    raise

        hookname = "pre_gitpull"
        exit_code = hooksObj.run_hook(hookname, data, args.directory)
        if exit_code != 0:
            raise ValueError('{} hook failed.'.format(hookname))

        # get/update target source(s)
        path = "{0}/{1}".format(args.directory, repo)
        if os.path.isdir(path):
            with chdir(path):
                exit_code = gitObj.gitPull(branch)
        else:
            with chdir('{0}'.format(args.directory)):
                exit_code = gitObj.gitShallowClone(repo, branch)

        if exit_code != 0:
            raise ValueError('gitpull failed.')

        hookname = "post_gitpull"
        exit_code = hooksObj.run_hook(hookname, data, args.directory)
        if exit_code != 0:
            raise ValueError('{} hook failed.'.format(hookname))

if __name__ == "__main__":
    settingObj = Settings()
    appObj = AppConfig()
    gitObj = GitUtils()
    hooksObj = Hooks()
    roger_gitpull = RogerGitPull()
    roger_gitpull.parser = roger_gitpull.parse_args()
    args = roger_gitpull.parser.parse_args()
    roger_gitpull.main(settingObj, appObj, gitObj, hooksObj, args)
