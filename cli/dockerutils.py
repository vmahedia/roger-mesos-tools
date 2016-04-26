#!/usr/bin/python

from __future__ import print_function
import os
import subprocess
import sys
from cli.appconfig import AppConfig
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


class DockerUtils:

    def docker_build(self, image_tag):
        exit_code = os.system('docker build -t {} .'.format(image_tag))
        if exit_code is not 0:
            raise ValueError("docker build failed")

    def docker_push(self, image):
        exit_code = os.system("docker push {0}".format(image))
        return exit_code
