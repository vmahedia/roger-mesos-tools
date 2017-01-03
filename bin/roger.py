#!/usr/bin/python

from __future__ import print_function

import os
import sys
import subprocess
import re
import importlib
from cli.utils import Utils


def print_help_opt(opt, desc):
    print("  {} {}".format(opt.ljust(13), desc))


def roger_help(root, commands):
    print("usage: roger [-h] [-v] command [arg...]\n")
    print("a command line interface to work with roger mesos.")
    print("\npositional arguments:")
    print_help_opt("command", "command to run.")
    print_help_opt("arg", "arguments to pass to the command.")
    print("\noptional arguments:")
    print_help_opt("-h, --help", "show this help message and exit.")
    print_help_opt("-v, --version", "show version information and exit.")
    print("\ncommands:")
    sys.path.append("{}/cli".format(root))
    for command in commands:
        description = ""
        module_name = "roger_" + command
        cmd_module = importlib.import_module(module_name)
        try:
            description = cmd_module.describe()
        except Exception as e:
            pass
        print_help_opt(command, description)
    print("\nrun: 'roger < command > -h' for more information on a command.")


def getFiles(directory):
    filenames = next(os.walk(directory))[2]
    return filenames


def getCommands(files):
    commands = set()
    for filename in files:
        if filename.startswith("roger_"):
            commands.add(re.split("roger_|\.", filename)[1])
    return sorted(commands)


def getScriptCall(root, command, command_args):
    script_call = "roger_{}.py".format(command)

    for command_arg in command_args:
        script_call = script_call + " {}".format(command_arg)
    return script_call


def main():
    root = ''
    utilsObj = Utils()
    own_dir = os.path.dirname(os.path.realpath(__file__))
    root = os.path.abspath(os.path.join(own_dir, os.pardir))
    files = getFiles("{}/cli/".format(root))
    commands = getCommands(files)
    if len(sys.argv) > 1:
        if sys.argv[1] == "-h" or sys.argv[1] == "--help":
            roger_help(root, commands)
        elif sys.argv[1] == "-v" or sys.argv[1] == "--version":
            version = utilsObj.roger_version(root)
            print(version)
        else:
            command = sys.argv[1]
            command_args = sys.argv[2:]
            if command in commands:
                print("root: {} command: {} args: {}".format(
                    root, command, command_args
                ))
                script_call = getScriptCall(root, command, command_args)
                os.system(script_call)
            else:
                raise SystemExit("Command is not valid. Exiting.")
    else:
        raise SystemExit("No arguments found. Please refer to usage: roger -h")

if __name__ == "__main__":
    main()
