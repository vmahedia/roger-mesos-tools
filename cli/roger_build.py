#!/usr/bin/python

from __future__ import print_function
import argparse
import json
import os
import sys
from cli.settings import Settings
from cli.appconfig import AppConfig
from cli.hooks import Hooks

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
    return 'runs the docker build and optionally pushes it into the registry.'


class RogerBuild(object):

    def parse_args(self):
        self.parser = argparse.ArgumentParser(
            prog='roger build', description=describe())
        self.parser.add_argument('app_name', metavar='app_name',
                                 help="application to build. Example: 'agora'.")
        self.parser.add_argument('directory', metavar='directory',
                                 help="working directory. Example: '/home/vagrant/work_dir'.")
        self.parser.add_argument('tag_name', metavar='tag_name',
                                 help="tag for the built image. Example: 'roger-collectd:0.20'.")
        self.parser.add_argument('config_file', metavar='config_file',
                                 help="configuration file to use. Example: 'content.json'.")
        self.parser.add_argument(
            '--push', '-p', help="Also push to registry. Defaults to false.", action="store_true")
        return self.parser

    def main(self, settingObj, appObj, hooksObj, args):
        config_dir = settingObj.getConfigDir()
        root = settingObj.getCliDir()
        config = appObj.getConfig(config_dir, args.config_file)
        roger_env = appObj.getRogerEnv(config_dir)

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

        projects = data.get('privateProjects', ['none'])
        projects = ','.join(projects)
        docker_path = data.get('path', 'none')

        # get/update target source(s)
        file_exists = True
        file_path = ''
        cur_dir = ''
        if "PWD" in os.environ:
            cur_dir = os.environ.get('PWD')
        abs_path = os.path.abspath(args.directory)
        repo_name = appObj.getRepoName(repo)
        if docker_path != 'none':
            if abs_path == args.directory:
                file_path = "{0}/{1}/{2}".format(args.directory,
                                                 repo_name, docker_path)
            else:
                file_path = "{0}/{1}/{2}/{3}".format(
                    cur_dir, args.directory, repo_name, docker_path)
        else:
            if abs_path == args.directory:
                file_path = "{0}/{1}".format(args.directory, repo_name)
            else:
                file_path = "{0}/{1}/{2}".format(cur_dir, args.directory, repo_name)

        hookname = "pre_build"
        exit_code = hooksObj.run_hook(hookname, data, file_path)
        if exit_code != 0:
            raise ValueError('{} hook failed.'.format(hookname))

        file_exists = os.path.exists("{0}/Dockerfile".format(file_path))

        if file_exists:
            if 'registry' not in roger_env:
                raise ValueError('Registry not found in roger-env.json file.')
            image = "{0}/{1}".format(roger_env['registry'], args.tag_name)
            try:
                if abs_path == args.directory:
                    exit_code = os.system("{0}/cli/docker_build.py '{1}' '{2}' '{3}' '{4}' '{5}'".format(
                        root, args.directory, repo, projects, docker_path, image))
                    if exit_code != 0:
                        raise ValueError(
                            'Docker build failed.')
                else:
                    exit_code = os.system("{0}/cli/docker_build.py '{1}/{2}' '{3}' '{4}' '{5}' '{6}'".format(
                        root, cur_dir, args.directory, repo, projects, docker_path, image))
                    if exit_code != 0:
                        raise ValueError(
                            'Docker build failed.')
                build_message = "Image {0} built".format(image)
                if(args.push):
                    exit_code = os.system("docker push {0}".format(image))
                    if exit_code != 0:
                        raise ValueError(
                            'Docker push failed.')
                    build_message += " and pushed to registry {}".format(roger_env[
                                                                         'registry'])
                print(build_message)
            except (IOError) as e:
                print("The folowing error occurred.(Error: %s).\n" %
                      e, file=sys.stderr)
                raise
        else:
            print("Dockerfile does not exist in dir: {}".format(file_path))

        hookname = "post_build"
        exit_code = hooksObj.run_hook(hookname, data, file_path)
        if exit_code != 0:
            raise ValueError('{} hook failed.'.format(hookname))

if __name__ == "__main__":
    settingObj = Settings()
    appObj = AppConfig()
    hooksObj = Hooks()
    roger_build = RogerBuild()
    roger_build.parser = roger_build.parse_args()
    args = roger_build.parser.parse_args()
    roger_build.main(settingObj, appObj, hooksObj, args)
