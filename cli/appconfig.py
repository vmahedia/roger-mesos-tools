#!/usr/bin/python

from __future__ import print_function
import os
import os.path
import sys
import json
import yaml
from cli.settings import Settings


class AppConfig:

    def __init__(self):
        self._config_file_path = ""

    @property
    def config_file_path(self):
        return self._config_file_path

    @config_file_path.setter
    def config_file_path(self, value):
        self._config_file_path = value

    def getRogerEnv(self, config_dir):
        roger_env = None
        env_file = '{0}/roger-mesos-tools.config'
        with open(env_file.format(config_dir)) as roger_env_file_obj:
            if env_file.lower().endswith('.config'):
                roger_env = yaml.load(roger_env_file_obj)
        return roger_env

    # (vmahedia) we should just take file as an argument and not directory
    # but for backward compatibility we have to keep it around for a while.
    # #backward-compatibility
    def getConfig(self, config_dir, config_file):
        config = None
        config_file_to_load = ""
        # Currently CLI reads a environment variable which has ROGER_CONFIG DIR so if the config file
        # is not defined on commandline with absolutey path, then it assumes config file must be
        # present on the path defined by env variable for ex. ROGER_CONFIG_DIR=/vagrant/config
        if os.path.isfile(config_file):
            config_file_to_load = config_file
        else:
            config_file_to_load = '{0}/{1}'.format(config_dir, config_file)

        # This is hacky but to maintain backward-compatibility, we need to keep the code above and also
        # support a new feature which lets customer put config file in their repo or anywhere else for
        # that we need to know the path - all the paths shouold be in the working directory if customers
        # expects us to locate the file within a repo.
        # so if the file is set through this class's property, that means we got it from commandline args
        # from user so use that one because it's explicit.
        if os.path.exists(self._config_file_path) and os.path.isfile(self._config_file_path):
            config_file_to_load = self._config_file_path

        with open(config_file_to_load) as config_file_obj:
            config = yaml.load(config_file_obj) if config_file.lower().endswith('.yml') else json.load(config_file_obj)
        return config

    def getAppData(self, config_dir, config_file, app_name):
        config = self.getConfig(config_dir, config_file)
        app_data = ''
        if app_name in config['apps']:
            app_data = config['apps'][app_name]
        return app_data

    def getRepoUrl(self, repo):
        if repo.startswith('git@github.com'):
            return repo
        else:
            settingObj = Settings()
            config_dir = settingObj.getConfigDir()
            roger_env = self.getRogerEnv(config_dir)
            if 'default_github_repo_prefix' in roger_env.keys():
                prefix = roger_env['default_github_repo_prefix']
            else:
                raise ValueError(
                    "Could not determine github repo.Please provide default \"github repo prefix\" or ensure repo startswith git@github.com")
            return str(prefix + '{}.git'.format(repo))

    def getRepoName(self, repo):
        if 'git@github' in repo:
            repo_name = repo.split("/")[1]
            repo_name = repo_name.split(".")[0]
            return str(repo_name)
        return repo
