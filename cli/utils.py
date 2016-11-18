#!/usr/bin/python

"""
Notes for Later:
* Better to return None rather than empty string or "special" string
* Return None or raise an exception if data passed in is not what you expect
* Prefer snake case for method names
* Better to pass in objects in the class constructor or method parameters rather
  than instantiate within the method. Harder to unit test if we don't.
* task_id_value ivar does not appear to be used within the class
* Keep line character length under 80
* generate_task_id_list nested too deep
"""

from __future__ import print_function
import os
import sys
import statsd
from cli.settings import Settings
from cli.appconfig import AppConfig
import hashlib
import time
import json
from pkg_resources import get_distribution


class Utils:

    def __init__(self):
        self.task_id_value = None

    def roger_version(self, root_dir):
        """
        Return the version

        root_dir [String] The root directory !Unclear!
        return   [String] Version of the tool

        Attempt to retrieve the package version from a
        pkg_resources.Distribution object. Otherwise, check for version in a
        VERSION file in the root directory.
        """
        version = "Unknown!"
        try:
            version = get_distribution('roger_mesos_tools').version
        except Exception:
            fname = os.path.join(root_dir, "VERSION")
            if(os.path.isfile(fname)):
                with open(os.path.join(root_dir, "VERSION")) as f:
                    version = f.read().strip()
        return version

    # Expected format:
    #   moz-content-kairos-7da406eb9e8937875e0548ae1149/v0.46
    def extractFullShaAndVersion(self, image):
        """
        Return the sha and version

        image  [String] The desired image
        return [String] sha and version

        If the string is "delimited" by hyphens, then return the last part of
        the string containing the sha and version. Otherwise, return an empty
        string.
        """
        if '-' not in image:
            return ''
        tokens = image.split('-')
        if len(tokens) != 0:
            return tokens[-1]
        else:
            return ''

    # Expected format:
    #   moz-content-kairos-7da406eb9e8937875e0548ae1149/v0.46
    def extractShaFromImage(self, image):
        """
        Return the sha from the image

        image  [String]: the desired image
        return [String]: The sha

        If the string is "delimited" by hyphens and contains `/v`, then split on
        `/v` and store result. Split the first member of the stored value by
        hyphen and return the last member of the result. Otherwise, return an
        empty string
        """
        if '/v' not in image:
            return ''
        sha = image.split('/v')
        if len(sha) != 0:
            sha = sha[0].split('-')
            if len(sha) != 0:
                return sha[-1]
        return ''

    def getStatsClient(self):
        """
        Return an instance of statsd.StatsClient

        return [statsd.StatsClient]

        The statsd.StatsClient passes in the statsd_url and statsd_port
        retrieved from the roger_env.
        """
        settingObj = Settings()
        appObj = AppConfig()
        config_dir = settingObj.getConfigDir()
        roger_env = appObj.getRogerEnv(config_dir)
        statsd_url = ""
        statsd_port = ""
        if 'statsd_endpoint' in roger_env.keys():
            statsd_url = roger_env['statsd_endpoint']
        if 'statsd_port' in roger_env.keys():
            statsd_port = int(roger_env['statsd_port'])
        return statsd.StatsClient(statsd_url, statsd_port)

    def get_identifier(self, config_name, user_name, app_name):
        """
        Generate an identifier based on the config_name, user_name and app_name

        config_name: [String] !Unclear!
        user_name:   [String] The desired user
        app_name:    [String] The desired application
        """
        hash_value = str(int(time.time())) + "-" + str(hashlib.sha224(config_name + "-" + user_name + "-" + app_name).hexdigest())[:8]
        return hash_value

    def extract_app_name(self, value):
        """
        !Outside of the method name, it is unclear what is actually happening
        aside from some string manipulation!

        value [String]: !Unclear!
        """
        if ':' in value:
            return value.split(":")[0]
        if '[' in value:
            return value.split("[")[0]
        return value

    def append_arguments(self, statsd_message_list, **kwargs):
        """
        statsd_message_list [?] Assumed to be a list of list of strings. !Unclear!

        For each item in statsd_message_list, store the input metric as the
        first member of said item and append the a comma separated string of
        key=value. Lastly, generate a tuple, with the first member being the
        aforementioned string and the second value being the second member of the
        item under iteration. Append said tupple to modified_message_list and
        return it. Raise an exception if something goes wrong.
        """
        modified_message_list = []
        try:
            for item in statsd_message_list:
                input_metric = item[0]
                for key, value in kwargs.iteritems():
                    input_metric += "," + key + "=" + value
                tup = (input_metric, item[1])
                modified_message_list.append(tup)
        except (Exception) as e:
            print("The following error occurred: %s" %
                  e, file=sys.stderr)
        return modified_message_list

    def modify_task_id(self, task_id_list):
        """
        Return a list of modified task ids

        task_id_list: !Unclear!

        For each task_id in the task_id_list, remove the first member in task_id
        if it contains a `/` and replace `/` with `_`. Append the result to the
        modified list and return it. Raise an exception if something goes wrong.
        """
        modified_task_id_list = []
        try:
            for task_id in task_id_list:
                if task_id[0] == '/':
                    task_id = task_id[1:]
                task_id = task_id.replace("/", "_")
                modified_task_id_list.append(task_id)
        except (Exception) as e:
            print("The following error occurred: %s" %
                  e, file=sys.stderr)
        return modified_task_id_list

    def generate_task_id_list(self, data):
        """
        Generates a list of task_ids based on data

        data [?] !Unclear!
        """
        task_id_list = []
        try:
            data_json = json.loads(data)
            top_level = ""
            if 'id' in data_json:
                top_level = data_json['id']
                if 'groups' in data_json:
                    for groups in data_json['groups']:
                        group_level = ""
                        if 'id' in groups:
                            group_level = groups['id']
                        if 'apps' in groups:
                            app_level = ""
                            for app in groups['apps']:
                                if type(app) == list:
                                    for item in app:
                                        if 'id' in item:
                                            app_level = item['id']
                                            task_id_list.append(str(top_level + "/" + group_level + "/" + app_level))
                                else:
                                    if 'id' in app:
                                        app_level = app['id']
                                        task_id_list.append(str(top_level + "/" + group_level + "/" + app_level))
                else:
                    task_id_list.append(str(top_level))
        except (Exception) as e:
            print("The following error occurred: %s" %
                  e, file=sys.stderr)
        return task_id_list

    def get_version(self):
        """
        Does the same thing as roger_version, but doesn't bother with the
        pkg_resources.Distribution object.
        """
        own_dir = os.path.dirname(os.path.realpath(__file__))
        root = os.path.abspath(os.path.join(own_dir, os.pardir))
        return self.roger_version(root)
