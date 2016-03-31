#!/usr/bin/env python

from __future__ import print_function
import os
import sys
from haproxyparser import HAProxyParser

class MarathonValidator:

  def check_path_begin_value(self, haproxy_parser_obj, environment, path_begin_value, acl_name):
    haproxy_parser_obj.parseConfig("dev")
    path_begin_values = haproxy_parser_obj.get_path_begin_values()

    if path_begin_value not in path_begin_values.keys():
      return True
    else:
      for key in path_begin_values.keys():
        if key == path_begin_value:
          if path_begin_values[key] == acl_name:
            return True
          else:
            print("\nPATH BEGIN value validation check failed. The PATH BEGIN '{}' you are trying " \
                 "to use is already in use by app id: '{}'".format(path_begin_value, path_begin_values[key]))
            print("The deployment will still happen if the --force-push flag is enabled.")
            return False

