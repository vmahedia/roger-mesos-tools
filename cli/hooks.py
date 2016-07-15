#!/usr/bin/python
from __future__ import print_function
from cli.utils import Utils
import os
import contextlib
import sys
from datetime import datetime
from cli.webhook import WebHook


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

    def __init__(self):
        self.utils = Utils()
        self.whobj = WebHook()

    def run_hook(self, hookname, appdata, path, hook_input_metric):
        try:
            exit_code = 0
            function_execution_start_time = datetime.now()
            execution_result = 'SUCCESS'
            envr = 'NA'
            print (appdata)
            print (appdata.keys())
            #import pdb; pdb.set_trace()
            temp = hook_input_metric.split(',')
            action, app_name, config_name, envr, user = temp[0], temp[1], temp[3], temp[4], temp[5]
            # expecting 'roger-tools.pre_push_time' extraction of pre_push as string from here
            action = ''.join(action.split('.')[1])
            action = '-'.join(action.split('_')[0:2])
            if ('post' in action):
                slackMessage = "Completed *" +action.split('-')[1] +"* of *" +app_name.split('=')[1]+ "* on *"+envr.split('=')[1]+"* (triggered by *"+ user.split('=')[1] +"*)"
                #slackMessage = user.split('=')[1]+' is Performing action: '+ action + ' on app: ' + app_name + ' in environment: '+ envr.split('=')[1]
                self.whobj.api_call(slackMessage,'#testhook')
            abs_path = os.path.abspath(path)
            if "hooks" in appdata and hookname in appdata["hooks"]:
                command = appdata["hooks"][hookname]
                with chdir(abs_path):
                    print("About to run {} hook [{}] at path {}".format(
                        hookname, command, abs_path))
                    exit_code = os.system(command)
        except (Exception) as e:
            print("The following error occurred: %s" %
                  e, file=sys.stderr)
            execution_result = 'FAILURE'
            raise
        finally:
            try:
                if 'execution_result' not in globals() or 'execution_result' not in locals():
                    execution_result = 'FAILURE'
                if 'function_execution_start_time' not in globals() or 'function_execution_start_time' not in locals():
                    function_execution_start_time = datetime.now()
                sc = self.utils.getStatsClient()
                time_take_milliseonds = ((datetime.now() - function_execution_start_time).total_seconds() * 1000)
                hook_input_metric = hook_input_metric + ",outcome=" + str(execution_result)
                sc.timing(hook_input_metric, time_take_milliseonds)
            except (Exception) as e:
                print("The following error occurred: %s" %
                      e, file=sys.stderr)
                raise
        return exit_code
