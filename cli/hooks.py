#!/usr/bin/python
from __future__ import print_function
import os
import contextlib


@contextlib.contextmanager
def chdir(dirname):
    '''Withable chdir function that restores directory'''
    curdir = os.getcwd()
    try:
        os.chdir(dirname)
        yield
    finally:
        os.chdir(curdir)


class Hooks:

    def run_hook(self, hookname, appdata, path):
        exit_code = 0
        abs_path = os.path.abspath(path)
        if "hooks" in appdata and hookname in appdata["hooks"]:
            command = appdata["hooks"][hookname]
            with chdir(abs_path):
                print("About to run {} hook [{}] at path {}".format(
                    hookname, command, abs_path))
                exit_code = os.system(command)

        return exit_code
