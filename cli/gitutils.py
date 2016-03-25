#!/usr/bin/python

from __future__ import print_function
import os
import subprocess
import sys

class GitUtils:

  def gitPull(self, branch):
    os.system("git pull origin {}".format(branch))

  def gitShallowClone(self, branch, repo):
    os.system("git clone --depth 1 --branch {} git@github.com:seomoz/{}.git".format(branch, repo))

  def gitClone(self, repo):
    os.system("git clone git@github.com:seomoz/{}.git".format(repo))

  def getGitSha(self, branch):
    proc = subprocess.Popen(
     ["git rev-parse origin/{} --verify HEAD".format(branch)],
     stdout=subprocess.PIPE, shell=True)
    out = proc.communicate()
    return out[0].split('\n')[0]
