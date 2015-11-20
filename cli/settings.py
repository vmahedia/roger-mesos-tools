#!/usr/bin/python

from __future__ import print_function
import os
import sys

class Settings:

  def getConfigDir(self):
    config_dir = ''
    if "ROGER_CONFIG_DIR" in os.environ:
      config_dir = os.environ.get('ROGER_CONFIG_DIR')
    if config_dir.strip() == '':
      sys.exit("Environment variable $ROGER_CONFIG_DIR is not set. Exiting.")
    config_dir = os.path.abspath(config_dir)
    return config_dir

  def getComponentsDir(self):
    comp_dir = ''
    if "ROGER_COMPONENTS_DIR" in os.environ:
      comp_dir = os.environ.get('ROGER_COMPONENTS_DIR')
    if comp_dir.strip() == '':
      sys.exit("Environment variable $ROGER_COMPONENTS_DIR is not set. Exiting.")
    comp_dir = os.path.abspath(comp_dir)
    return comp_dir

  def getTemplatesDir(self):
    templ_dir = ''
    if "ROGER_TEMPLATES_DIR" in os.environ:
      templ_dir = os.environ.get('ROGER_TEMPLATES_DIR')
    if templ_dir.strip() == '':
      sys.exit("Environment variable $ROGER_TEMPLATES_DIR is not set.Exiting.")
    return templ_dir

  def getSecretsDir(self):
    secrets_dir = ''
    if "ROGER_SECRETS_DIR" in os.environ:
      secrets_dir = os.environ.get('ROGER_SECRETS_DIR')
    if secrets_dir.strip() == '':
      sys.exit("Environment variable $ROGER_SECRETS_DIR is not set. Exiting.")
    secrets_dir = os.path.abspath(secrets_dir)
    return secrets_dir

  def getCliDir(self):
    cli_dir = ''
    if "ROGER_CLI_ROOT_DIR" in os.environ:
      cli_dir = os.environ.get('ROGER_CLI_ROOT_DIR')
    if cli_dir.strip() == '':
      sys.exit("Environment variable $ROGER_CLI_ROOT_DIR is not set. Exiting.")
    cli_dir = os.path.abspath(cli_dir)
    return cli_dir
