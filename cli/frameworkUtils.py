#!/usr/bin/python

from __future__ import print_function
import os
import sys
from cli.marathon import Marathon
from cli.chronos import Chronos


class FrameworkUtils:

    def __init__(self):
        self.framework = None

    def setFramework(self, framework):
        self.framework = framework

    def getFramework(self, data):
        if self.framework is not None:
            return self.framework
        else:
            if 'framework' in data:
                if data['framework'].lower() == "chronos":
                    return Chronos()
            return Marathon()
