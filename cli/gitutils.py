#!/usr/bin/python

from __future__ import print_function
import os
import subprocess
import sys

import contextlib

@contextlib.contextmanager
def chdir(dirname):
  '''Withable chdir function that restores directory'''
  curdir = os.getcwd()
  try:
    os.chdir(dirname)
    yield
  finally: os.chdir(curdir)

class GitUtils:

  def gitPull(self, branch):
    os.system("git pull origin {}".format(branch))

  def gitShallowClone(self, repo, branch):
    os.system("git clone --depth 1 --branch {} git@github.com:seomoz/{}.git".format(branch, repo))

  def gitClone(self, repo, branch):
    os.system("git clone --branch {} git@github.com:seomoz/{}.git".format(branch, repo))

  def getGitSha(self, repo, branch, work_dir):
    with chdir("{0}/{1}".format(work_dir, repo)):
      proc = subprocess.Popen(
          ["git rev-parse origin/{} --verify HEAD".format(branch)],
          stdout=subprocess.PIPE, shell=True)

      out = proc.communicate()
      return out[0].split('\n')[0]
