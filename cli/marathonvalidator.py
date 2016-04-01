#!/usr/bin/env python

from __future__ import print_function
import os
import sys
from haproxyparser import HAProxyParser

class MarathonValidator:

  def validate(self, haproxy_parser_obj, environment, path_begin_value, acl_name):
    haproxy_parser_obj.parseConfig("dev")
    result = self.check_path_begin_value(haproxy_parser_obj, environment, path_begin_value, acl_name)
    return result

  def check_path_begin_value(self, haproxy_parser_obj, environment, path_begin_value, acl_name):
    path_begin_values = haproxy_parser_obj.get_path_begin_values()

    if path_begin_value not in path_begin_values.keys():
      return True
    else:
      for key in path_begin_values.keys():
        if key == path_begin_value:
          if path_begin_values[key] == acl_name:
            return True
          else:
            print("\nHTTP PREFIX validation check failed. The HTTP PREFIX '{}' you are trying " \
                 "to use is already in use by app id: '{}'".format(path_begin_value, path_begin_values[key]))
            return False

