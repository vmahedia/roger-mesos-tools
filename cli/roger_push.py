#!/usr/bin/python

from __future__ import print_function
import argparse
from jinja2 import Environment, FileSystemLoader, StrictUndefined, exceptions
from datetime import datetime
import requests
import json
import os
import sys
import traceback
import logging
from cli.settings import Settings
from cli.appconfig import AppConfig
from cli.marathon import Marathon
from cli.hooks import Hooks
from cli.chronos import Chronos
from cli.frameworkUtils import FrameworkUtils

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

def describe():
    return 'pushes the application into roger mesos.'

class RogerPushArgParser(argparse.ArgumentParser):
    '''ArgumentParser with all the Roger Args loaded. Run parse_args() on a
    new instance to parse args from command-line.'''

    def __init__(self):
        super(RogerPushArgParser, self).__init__(
                prog='roger push', description=describe())
        parser.add_argument('app_name', metavar='app_name', help="application to push. Can also push specific" \
                " containers(comma separated). Example: 'agora' or 'app_name:container1,container2'")
        parser.add_argument('-e', '--env', metavar='env',
                help="environment to push to. Example: 'dev' or 'prod'")
        parser.add_argument('directory', metavar='directory',
                help="working directory. Example: '/home/vagrant/work_dir'")
        parser.add_argument('image_name', metavar='image_name',
                help="image name that includes version to use. Example: 'roger-collectd-v0.20' or 'elasticsearch-v0.07'")
        parser.add_argument('config_file', metavar='config_file',
                help="configuration file to use. Example: 'content.json' or 'kwe.json'")
        parser.add_argument(
                '--skip-push', '-s', help="skips push. Only generates components for review. Defaults to false.", action="store_true")
        parser.add_argument(
                '--force-push', '-f', help="force push. Not Recommended. Forces push even if validation checks failed. Defaults to false.", action="store_true")
        parser.add_argument('--secrets-file', '-S',
                help="specifies an optional secrets file for deploy runtime variables.")


class RogerPush(object):
    def __init__(self, settings, appConfig, frameworkObject, hooksObj, args):
        self.settings = settings
        self.appConfig = appConfig
        self.frameworkObject = frameworkObject
        self.hooksObj = hooksObj
        self.args = args

    def loadSecretsJson(self, secrets_dir, json_file_name, environment):
        if self.args.secrets_file is not None:
            print("Using specified secrets file: {}".format(self.args.secrets_file))
            json_file_name = self.args.secrets_file
        exists = os.path.exists(secrets_dir)
        if exists is False:
            os.makedirs(secrets_dir)

        # Two possible paths -- first without environment, second with
        path1 = "{}/{}".format(secrets_dir, json_file_name)
        path2 = "{}/{}/{}".format(secrets_dir, environment, json_file_name)
        print(" Loading secrets from {} or {}".format(path1, path2))

        try:
            with open(path1) as f:
                return json.load(f)
        except IOError:
            pass
        except ValueError as e:
            raise ValueError(
                " Error while loading json from {} - {}".format(path1, e))

        try:
            with open(path2) as f:
                return json.load(f)
        except IOError:
            print(" Couldn't load secrets file environment in %s or %s\n" %
                  (path1, path2), file=sys.stderr)
            return {}
        except ValueError as e:
            raise ValueError(
                " Error while loading json from {} - {}".format(path2, e))

    def replaceSecrets(self, output_dict, secrets_dict):
        if type(output_dict) is not dict:
            return output_dict

        for key in output_dict:
            if output_dict[key] == "SECRET":
                if key in secrets_dict.keys():
                    output_dict[key] = secrets_dict[key]

            if type(output_dict[key]) is list:
                temp_list = []
                for list_elem in output_dict[key]:
                    temp_list.append(self.replaceSecrets(
                        list_elem, secrets_dict))
                    output_dict[key] = temp_list

            if type(output_dict[key]) is dict:
                temp_dict = self.replaceSecrets(output_dict[key], secrets_dict)
                output_dict[key] = temp_dict

        return output_dict

    def mergeSecrets(self, json_str, secrets):
        '''Given a JSON string and an object of secret environment variables, replaces
        parses the JSON keys with the secret variables. Returns back
        a JSON string. Raises an error if there are any SECRET variables still exists.'''
        output_dict = json.loads(json_str)
        json_str = json.dumps(self.replaceSecrets(
            output_dict, secrets), indent=4)

        if '\"SECRET\"' in json_str:
            print('There are still "SECRET" values -- does your secrets file have all secret environment variables?')
            return "StandardError"
        return json_str

    def renderTemplate(self, template, environment, image, app_data, config, container, failed_container_dict, container_name, extra_vars):
        variables = { 'environment': environment, 'image': image }

        # Copy variables from config-wide, app-wide, then container-wide variable
        # configs, each one from "global" and then environment-specific.
        for obj in [config, app_data, container]:
            if type(obj) == dict and 'vars' in obj:
                variables.update(obj['vars'].get('global', {}))
                variables.update(obj['vars'].get('environment', {}).get(environment, {}))

        variables.update(extra_vars)

        try:
            return template.render(variables)
        except exceptions.UndefinedError as e:
            error_str = "The following error occurred. %s.\n" % e
            print(error_str, file=sys.stderr)
            failed_container_dict[container_name] = error_str
            return ''


    def repo_relative_path(self, repo, path):
        '''Returns a path relative to the repo, assumed to be under [args.directory]/[repo name]'''
        repo_name = self.appConfig.getRepoName(repo)
        abs_path = os.path.abspath(self.args.directory)
        if abs_path == self.args.directory:
            return "{0}/{1}/{2}".format(self.args.directory, repo_name, path)
        else:
            return "{0}/{1}/{2}/{3}".format(os.environ.get('PWD', ''),
                    self.args.directory, repo_name, data['template_path'])


    def main(self):
        # TODO: most of this function is just setting various variables (environment, repo, data, extra_vars)...
        # It would be great to break this out into memoized environment(), repo(), etc. functions

        config_dir = self.settings.getConfigDir()

        config = self.appConfig.getConfig(config_dir, self.args.config_file)
        roger_env = self.appConfig.getRogerEnv(config_dir)

        if 'registry' not in roger_env.keys():
            raise ValueError(
                'Registry not found in roger-env.json file.')
        environment = roger_env.get('default', '')
        if self.args.env is None:
            if "ROGER_ENV" in os.environ:
                env_var = os.environ.get('ROGER_ENV')
                if env_var.strip() == '':
                    print(
                        "Environment variable $ROGER_ENV is not set. Using the default set from roger-env.json file")
                else:
                    print(
                        "Using value {} from environment variable $ROGER_ENV".format(env_var))
                    environment = env_var
        else:
            environment = self.args.env

        if environment not in roger_env['environments']:
            raise ValueError(
                'Environment not found in roger-env.json file.')

        environmentObj = roger_env['environments'][environment]
        app_name = self.args.app_name
        container_list = []
        if ':' in app_name:
            tokens = app_name.split(':')
            app_name = tokens[0]
            if ',' in tokens[1]:
                container_list = tokens[1].split(',')
            else:
                container_list.append(tokens[1])

        data = self.appConfig.getAppData(config_dir, self.args.config_file, app_name)
        if not data:
            raise ValueError('Application with name [{}] or data for it not found at {}/{}.'.format(
                app_name, config_dir, self.args.config_file))

        configured_container_list = []
        for task in data['containers']:
            if type(task) == dict:
                configured_container_list.append(task.keys()[0])
            else:
                configured_container_list.append(task)
        if not set(container_list) <= set(configured_container_list):
            raise ValueError('List of containers [{}] passed do not match list of acceptable containers: [{}]'.format(container_list, configured_container_list))

        frameworkObj = self.frameworkObject.getFramework(data)
        framework = frameworkObj.getName()

        repo = data.get('repo', config.get('repo', app_name))

        comp_dir = self.settings.getComponentsDir()
        templ_dir = self.settings.getTemplatesDir()
        secrets_dir = self.settings.getSecretsDir()

        # template marathon files
        if not container_list:
            data_containers = data['containers']
        else:
            data_containers = container_list

        failed_container_dict = {}

        for container in data_containers:
            if type(container) == dict:
                container_name = str(container.keys()[0])
                container = container[container_name]
                containerConfig = "{0}-{1}.json".format(
                    config['name'], container_name)
            else:
                container_name = container
                containerConfig = "{0}-{1}.json".format(
                    config['name'], container)

            # Required for when work_dir,component_dir,template_dir or
            # secret_env_dir is something like '.' or './temp"
            # TODO: this seems like a weird choice of default relative path, and
            # is awkward here as it gives this function a side-effect. Also I don't see how
            # it is doing what the comment says it is, as os.chdir does not effect PWD env var
            # used in self.repo_relative_path.
            os.chdir(os.path.dirname(os.path.realpath(__file__)))

            if 'template_path' in data:
                app_path = self.repo_relative_path(repo, data['template_path'])
            else:
                app_path = templ_dir

            if not app_path.endswith('/'):
                app_path = app_path + '/'

            env = Environment(loader=FileSystemLoader(
                "{}".format(app_path)), undefined=StrictUndefined)
            template_with_path = "[{}{}]".format(app_path, containerConfig)
            try:
                template = env.get_template(containerConfig)
            except exceptions.TemplateNotFound as e:
                raise ValueError(
                    "The template file {} does not exist".format(template_with_path))
            except Exception as e:
                raise ValueError(
                    "Error while reading template from {} - {}".format(template_with_path, e))

            image_path = "{0}/{1}".format(
                roger_env['registry'], self.args.image_name)
            print("Rendering content from template {} for environment [{}]".format(
                template_with_path, environment))
            output = self.renderTemplate(
                template, environment, image_path, data, config, container, failed_container_dict, container_name)
            # Adding check to see if all jinja variables git resolved fot the
            # container
            if container_name not in failed_container_dict:
                # Adding check so that not all apps try to mergeSecrets
                try:
                    outputObj = json.loads(output)
                except Exception as e:
                    raise ValueError(
                        "Error while loading json from {} - {}".format(template_with_path, e))

                if 'SECRET' in output:
                    output = self.mergeSecrets(output, self.loadSecretsJson(
                        secrets_dir, containerConfig, environment))
                if output != "StandardError":
                    try:
                        comp_exists = os.path.exists("{0}".format(comp_dir))
                        if comp_exists is False:
                            os.makedirs("{0}".format(comp_dir))
                        comp_env_exists = os.path.exists(
                            "{0}/{1}".format(comp_dir, environment))
                        if comp_env_exists is False:
                            os.makedirs(
                                "{0}/{1}".format(comp_dir, environment))
                    except Exception as e:
                        logging.error(traceback.format_exc())
                    with open("{0}/{1}/{2}".format(comp_dir, environment, containerConfig), 'wb') as fh:
                        fh.write(output)

        hookname = "pre_push"
        exit_code = self.hooksObj.run_hook(hookname, data, app_path)
        if exit_code != 0:
            raise ValueError('{} hook failed.'.format(hookname))

        if self.args.skip_push:
            print("Skipping push to {} framework. The rendered config file(s) are under {}/{}".format(
                framework, comp_dir, environment))
        else:
            # push to roger framework
            for container in data_containers:
                if type(container) == dict:
                    container_name = str(container.keys()[0])
                    containerConfig = "{0}-{1}.json".format(
                        config['name'], container_name)
                else:
                    container_name = container
                    containerConfig = "{0}-{1}.json".format(
                        config['name'], container)

                if container_name in failed_container_dict:
                    print("Failed push to {} framework for container {} as unresolved Jinja variables present in template.".format(
                        framework, container))
                else:
                    config_file_path = "{0}/{1}/{2}".format(
                        comp_dir, environment, containerConfig)

                    result = frameworkObj.runDeploymentChecks(
                        config_file_path, environment)

                    if self.args.force_push or result is True:
                        frameworkObj.put(
                            config_file_path, environmentObj, container_name, environment)
                    else:
                        print("Skipping push to {} framework for container {} as Validation Checks failed.".format(
                            framework, container))

        hookname = "post_push"
        exit_code = self.hooksObj.run_hook(hookname, data, app_path)
        if exit_code != 0:
            raise ValueError('{} hook failed.'.format(hookname))


if __name__ == "__main__":
    settingObj = Settings()
    appObj = AppConfig()
    frameworkUtils = FrameworkUtils()
    hooksObj = Hooks()
    args = RogerPushArgParser().parse_args()
    RogerPush(settingObj, appObj, frameworkUtil, hooksObj, args).main()
