#!/usr/bin/env python

from __future__ import print_function
import os
import sys
from haproxyparser import HAProxyParser

class MarathonValidator:

  def check_http_prefix(self, environment, http_prefix, app_id):
    haproxy_parser_obj = HAProxyParser()
    haproxy_parser_obj.parseConfig("dev")
    http_prefixes = haproxy_parser_obj.get_http_prefixes()

    if http_prefix not in http_prefixes.keys():
      return True
    else:
      for key in http_prefixes.keys():
        if key == http_prefix:
          if http_prefixes[key] == app_id:
            return True
          else:
            print("\nHTTP PREFIX validation check failed. The HTTP_PREFIX you are trying " \
                 "to use is already in use by app id: {}".format(http_prefixes[key]))
            print("The deployment will still happen if the --force-push flag is enabled.")
            return False

