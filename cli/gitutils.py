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


class GitUtils:

    def gitPull(self, branch, verbose):
        redirect = " >/dev/null 2>&1"
        if verbose:
            redirect = ""
        exit_code = os.system("git pull origin {} {}".format(branch, redirect))
        return exit_code

    def gitShallowClone(self, repo, branch, verbose):
        appObj = AppConfig()
        try:
            repo_url = appObj.getRepoUrl(repo)
        except (ValueError) as e:
            print("The folowing error occurred.(Error: %s).\n" %
                  e, file=sys.stderr)
        redirect = " >/dev/null 2>&1"
        if verbose:
            redirect = ""
        exit_code = os.system(
            "git clone --depth 1 --branch {} {} {}".format(branch, repo_url, redirect))
        return exit_code

    def gitClone(self, repo, branch):
        appObj = AppConfig()
        try:
            repo_url = appObj.getRepoUrl(repo)
        except (ValueError) as e:
            print("The folowing error occurred.(Error: %s).\n" %
                  e, file=sys.stderr)
        exit_code = os.system(
            "git clone --branch {} {}".format(branch, repo_url))
        return exit_code

    def getGitSha(self, repo, branch, work_dir):
        appObj = AppConfig()
        repo_name = appObj.getRepoName(repo)
        with chdir("{0}/{1}".format(work_dir, repo_name)):
            proc = subprocess.Popen(
                ["git rev-parse origin/{} --verify HEAD".format(branch)],
                stdout=subprocess.PIPE, shell=True)

            out = proc.communicate()
            return out[0].split('\n')[0]
