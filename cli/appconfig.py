#!/usr/bin/python

"""
Notes for later
* Class doesn't carry state
  * Either make the method class methods or remove the class all together
* Snake care preferred over camel case for method names
* Best to pass the format method to strings earlier than later
* Better to return None than empty string
* Better to pass in objects instead of instantiating them within the method
  definition. If you don't do this, it makes it hard to unit test. You can do
  this in the class constructor or as a method parameter.
* Keep strings length under 80 characters.

"""

from __future__ import print_function
import os
import os.path
import sys
import json
import yaml
from cli.settings import Settings


class AppConfig:

    def getRogerEnv(self, config_dir):
        """
        Return the Roger environment

        config_dir: [String] Path to the configuration directory
        return:     [Dict]   Roger environment data

        Parse the the roger-mesos-tools.config for the given config dir and load
        the yaml as a dict.
        """
        roger_env = None
        env_file = '{0}/roger-mesos-tools.config'
        with open(env_file.format(config_dir)) as roger_env_file_obj:
            if env_file.lower().endswith('.config'):
                roger_env = yaml.load(roger_env_file_obj)
        return roger_env

    def getConfig(self, config_dir, config_file):
        """
        Return the config !What config?!

        config_dir:  [String] Path to the configuration directory
        config_file: [String] The configuration file

        If the config file exists, load it as yaml if ending in a yml extension.
        Otherwise, load as json. If the config file doesn't exist, generate a
        path to the file comprised of the config dir and the config file. Apply
        the aforementioned logic.
        """
        config = None
        if os.path.exists(config_file):
            with open(config_file) as config_file_obj:
                config = yaml.load(config_file_obj) if config_file.lower(
                ).endswith('.yml') else json.load(config_file_obj)
        else:
            with open('{0}/{1}'.format(config_dir, config_file)) as config_file_obj:
                config = yaml.load(config_file_obj) if config_file.lower(
                ).endswith('.yml') else json.load(config_file_obj)
        return config

    def getAppData(self, config_dir, config_file, app_name):
        """
        Return the the application data

        config_dir:  [String] Path to the configuration directory
        config_file: [String] The config file
        app_name:    [String] Name of the specified application
        return:      [?]      This could be any type. Please specify

        Get the config as a dict. If app name is a key in the apps key, then
        return the value at said key.
        """
        config = self.getConfig(config_dir, config_file)
        app_data = ''
        if app_name in config['apps']:
            app_data = config['apps'][app_name]
        return app_data

    def getRepoUrl(self, repo):
        """
        Return the url for the repo

        repo   [String]: The github repository URL
        return [String]: The valid github repository URL

        If the URL implicitly uses SSH as the protocol, which can be identified
        by the prefix `git@`, then return the value of repo. Otherwise, retrieve
        the config_dir and roger_env via cli.Settings instance. If the
        'default_github_repo_prefix' is a found key in roger env, then set the
        prefix to the value of said key and return a repo generated from said
        value. Otherwise, raise a ValueError.
        """
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
        """
        Return the repo name

        repo   [String]: the repo url
        return [String]: the repo name

        if `git@github` is in the value of repo, then retrieve the first path
        value without dot characters. Otherwise, return the value of repo as is.
        """
        if 'git@github' in repo:
            repo_name = repo.split("/")[1]
            repo_name = repo_name.split(".")[0]
            return str(repo_name)
        return repo
