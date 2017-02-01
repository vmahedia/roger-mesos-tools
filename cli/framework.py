#!/usr/bin/python

from __future__ import print_function
import os
import sys
import yaml

from jinja2 import Environment, FileSystemLoader
from cli.settings import Settings
from abc import ABCMeta, abstractmethod

settings = Settings()


class Framework(object):
    __metaclass__ = ABCMeta

    def fetchUserPass(self, env):
        if self.user is None:
            self.user = settings.getUser()
        if self.passw is None:
            self.passw = settings.getPass(env)
        print("Using u:{}, p:****".format(self.user))

    def app_id(self, template_file, framework):
        """
        returns the application id for the given template file

        :params:
        :template_file [str]: absoulte path to the template file
        :framework: [str]: name of framework Marathon or Chronos
        :return: [dict]
        """
        if framework == "Marathon":
            key = "id"
        elif framework == "Chronos":
            key = "name"
        dir_name = os.path.dirname(template_file)
        file_name = os.path.basename(template_file)
        env = Environment(loader=FileSystemLoader(dir_name))
        template = env.get_template(file_name)
        return yaml.safe_load(str(template.module))[key]

    @abstractmethod
    def getName(self):
        pass

    @abstractmethod
    def get(self, roger_env, environment):
        pass

    @abstractmethod
    def put(self, file_path, environmentObj, container, environment, act_as_user):
        pass

    @abstractmethod
    def runDeploymentChecks(self, file_path, environment):
        pass

    @abstractmethod
    def getCurrentImageVersion(self, roger_env, environment, application):
        pass

    @abstractmethod
    def getTasks(self, roger_env, environment):
        pass

    @abstractmethod
    def get_image_name(self, environment, application):
        pass
