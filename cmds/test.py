#!/usr/bin/python

from __future__ import print_function
from tempfile import mkdtemp
import argparse
from decimal import *
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import subprocess
import json
import os
import requests
import sys
import re
import shutil
from settings import Settings
from appconfig import AppConfig 
#settings = settings.Settings()

def main():
  config_dir = setObj.getConfigDir()
  if config_dir.strip() == '':
    sys.exit("Environment variable $ROGER_CONFIG_DIR is not set")
  config_dir = os.path.abspath(config_dir)
  print(config_dir)

  print("Test app config")
  rogerenv = appObj.getRogerEnv(config_dir)
  print(rogerenv)
  appObj.getAppData(config_dir, "roger.json", "grafana")

if __name__ == "__main__":
  setObj = Settings()
  appObj = AppConfig()
  main()
