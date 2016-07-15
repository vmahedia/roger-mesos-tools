#!/usr/bin/python
from __future__ import print_function
import os
import contextlib
import sys
from sets import Set
from datetime import datetime
from cli.webhook import WebHook
from cli.utils import Utils


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

    flag = False

    def __init__(self):
        self.utils = Utils()
        self.whobj = WebHook()

    def run_hook(self, hookname, appdata, path, hook_input_metric):
        try:
            exit_code = 0
            function_execution_start_time = datetime.now()
            defChannel = '#rogeros-deploy'
            execution_result = 'SUCCESS'
            message = 'default message'
            envr = 'NA'
            temp = hook_input_metric.split(',')
            action, app_name, config_name, envr, user = temp[0], temp[1], temp[3], temp[4], temp[5]
            action = ''.join(action.split('.')[1])
            action = '-'.join(action.split('_')[0:2])
            try:
                channelsSet = Set(appdata['notifications']['channels'])
                envSet = Set(appdata['notifications']['envs'])
                commandsSet = Set(appdata['notifications']['commands'])
                if len(channelsSet) == 0 or len(envSet) == 0 or len(commandsSet) == 0: # to handle no tag at all
                    message = str('*Switching to defaults*: All environments, all actions')
                    if self.flag is False:
                        self.whobj.api_call(message,defChannel) # Default message  to slack channel just once
                    channelsSet = [defChannel]
                    envSet = ['dev', 'production', 'staging', 'local'] # default as e
                    commandsSet = ['pull','build', 'push']
                    self.flag = True

                if list(envSet)[0] == 'all':
                    envSet = ['dev', 'production', 'staging', 'local'] # to handle all tag

                if list(commandsSet)[0] == 'all':
                    commandsSet = ['pull','build', 'push'] # to handle all tag

            except (Exception) as e:
                self.whobj.api_call("The following error occurred : %s" %e , defChannel)
                print("The following error occurred: %s" %
                      e, file=sys.stderr)
                raise

            if ('post' in action and envr.split('=')[1] in envSet and action.split('-')[1] in commandsSet):
                for channel in channelsSet:
                    slackMessage = ("Completed *" +action.split('-')[1] +"* of *" +app_name.split('=')[1]+
                    "* on *"+envr.split('=')[1]+ "* in *" +
                    str((datetime.now() - function_execution_start_time).total_seconds()*1000) +
                    "* miliseconds (triggered by *"+ user.split('=')[1] +"*)")
                    self.whobj.api_call(slackMessage,'#'+channel)
            abs_path = os.path.abspath(path)
            if "hooks" in appdata and hookname in appdata["hooks"]:
                command = appdata["hooks"][hookname]
                with chdir(abs_path):
                    print("About to run {} hook [{}] at path {}".format(
                        hookname, command, abs_path))
                    exit_code = os.system(command)
        except (Exception) as e:
            print("The following error occurred : %s" %
                  e, file=sys.stderr)
            execution_result = 'FAILURE'
            self.whobj.api_call("The following error occurred : %s" %e ,defChannel)
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
