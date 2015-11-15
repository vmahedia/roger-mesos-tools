#!/usr/bin/python

from __future__ import print_function
import os
import sys

class Settings:

  def getConfigDir(self):
    config_dir = ''
    if "ROGER_CONFIG_DIR" in os.environ:
      config_dir = os.environ.get('ROGER_CONFIG_DIR')
    return config_dir

  def getComponentsDir(self):
    comp_dir = ''
    if "ROGER_COMPONENTS_DIR" in os.environ:
      comp_dir = os.environ.get('ROGER_COMPONENTS_DIR')
    return comp_dir

  def getTemplatesDir(self):
    templ_dir = ''
    if "ROGER_TEMPLATES_DIR" in os.environ:
      templ_dir = os.environ.get('ROGER_TEMPLATES_DIR')
    return templ_dir

  def getSecretsDir(self):
    secrets_dir = ''
    if "ROGER_SECRETS_DIR" in os.environ:
      secrets_dir = os.environ.get('ROGER_SECRETS_DIR')
    return secrets_dir
