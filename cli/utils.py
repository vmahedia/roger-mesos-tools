#!/usr/bin/python

from __future__ import print_function
import os
import sys

class Utils:

  # Expected format:
  #   moz-content-kairos-7da406eb9e8937875e0548ae1149/v0.46
  def extractFullShaAndVersion(image):
    return image.split('-')[3]

  # Expected format:
  #   moz-content-kairos-7da406eb9e8937875e0548ae1149/v0.46
  def extractShaFromImage(image):
    sha = image.split('/')
    if sha != None and sha[1] != None:
      sha = sha[1].split('-')
      if sha[3] != None:
        return sha[3]
    return ''
