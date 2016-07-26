import slackweb
from sets import Set
from datetime import datetime
from slackclient import SlackClient

from cli.settings import Settings
from cli.appconfig import AppConfig


class WebHook:

    def __init__(self):
        self.disabled = True
        self.emoji = ':rocket:'
        self.defChannel = ''
        self.username = 'rogeros-deploy-bot'
        self.settingObj = Settings()
        self.appconfigObj = AppConfig()

    def webhookSetting(self):
        try:
            config_dir = self.settingObj.getConfigDir()
            roger_env = self.appconfigObj.getRogerEnv(config_dir)
            if 'slack_webhook_url' in roger_env.keys():
                self.webhookURL = roger_env['slack_webhook_url']
            if 'slack_api_token' in roger_env.keys():
                self.token = roger_env['slack_api_token']
            if 'slack_default_channel' in roger_env.keys():
                self.defChannel = roger_env['slack_default_channel']
            if 'slack_deploy_botid' in roger_env.keys():
                self.botid = roger_env['slack_deploy_botid']
        except (Exception) as e:
            print("Warning: slackweb basic initialization failed (error: %s).\
            Not using slack." % e)
            return
        try:
            self.sc = SlackClient(self.token)
            self.client = slackweb.Slack(url=self.webhookURL)
            self.disabled = False
        except (Exception) as e:
            print("Warning: slackweb basic initialization failed (error: %s).\
            Not using slack." % e)
            return  # disabled flag remains False

    def custom_api_call(self, text, channel):
        self.webhookSetting()
        if len(channel) == 0:
            channel = self.defChannel
        var = self.sc.api_call("channels.list")
        length = len(var['channels'])
        for iterator in range(0, length):
            # getting rid of # for comparison
            if channel[1:] == var['channels'][iterator]['name']:
                if self.botid in var['channels'][iterator]['members']:
                    if not self.disabled:
                        self.client.notify(channel=channel, username=self.username,
                                           icon_emoji=self.emoji, text=text)

    def invoke_webhook(self, appdata, hook_input_metric):
        function_execution_start_time = datetime.now()
        self.webhookSetting()
        try:
            action = app_name = envr = user = ''
            temp = hook_input_metric.split(',')
            for var in temp:
                varAnother = var.split('=')[0]
                if varAnother == 'event':
                    action = var.split('=')[1]
                    continue

                if varAnother == 'app_name':
                    app_name = var.split('=')[1]
                    continue

                if varAnother == 'env':
                    envr = var.split('=')[1]
                    continue

                if varAnother == 'user':
                    user = var.split('=')[1]
                    continue
            if len(action) == 0 or len(app_name) == 0 or len(envr) == 0 or len(user) == 0:
                raise ValueError

        except (Exception, KeyError, ValueError, IndexError) as e:
            print("The following error occurred: %s" %
                  e)
            raise
        try:
            if 'notifications' in appdata:
                channelsSet = Set(appdata['notifications']['channels'])
                envSet = Set(appdata['notifications']['envs'])
                commandsSet = Set(appdata['notifications']['commands'])
                # to handle no tag at all
                if (len(channelsSet) == 0 or len(envSet) == 0 or len(commandsSet) == 0):
                    return
            else:
                return
            # to handle all tag for env and commands
            if list(envSet)[0] == 'all':
                envSet = ['dev', 'production', 'staging', 'local']

            if list(commandsSet)[0] == 'all':
                commandsSet = ['pull', 'build', 'push']
        except (Exception, KeyError, ValueError) as e:
            # notify to channel and log it as well
            print("The following error occurred: %s" %
                  e)
            raise
        try:
            if ('post' in action and envr in envSet and action.split('_')[1] in commandsSet):
                for channel in channelsSet:
                    timeElapsed = '{0:.2f}'.format((datetime.now() - function_execution_start_time).total_seconds() * 1000)
                    unit = 'miliseconds'
                    slackMessage = ("Completed *" + action.split('_')[1] + "* of *" + app_name + "* on *" + envr + "* in *" + str(timeElapsed) + "* " + unit + " (triggered by *" + user + "*)")
                    self.custom_api_call(slackMessage, '#' + channel)
        except (Exception) as e:
            self.custom_api_call("The following error occurred: %s" % e, self.defChannel)
            print("The following error occurred: %s" %
                  e)
            raise
