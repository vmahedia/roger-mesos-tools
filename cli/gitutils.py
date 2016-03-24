#!/usr/bin/python

from __future__ import print_function
import os
import sys

class GitUtils:

  def gitPull(self, branch):
    os.system("git pull origin {}".format(branch))

  def gitClone(self, branch, repo):
    os.system("git clone --depth 1 --branch {} git@github.com:seomoz/{}.git".format(branch, repo))
