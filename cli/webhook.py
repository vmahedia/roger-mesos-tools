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
        self.config_dir = ''
        self.username = 'rogeros-deploy-bot'
        self.settingObj = Settings()
        self.appconfigObj = AppConfig()
        self.configLoadFlag = False
        self.config = ''
        self.config_channels = []
        self.config_envs = []
        self.config_commands = []

    def webhookSetting(self):
        try:
            self.config_dir = self.settingObj.getConfigDir()
            roger_env = self.appconfigObj.getRogerEnv(self.config_dir)
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
        try:
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
        except (Exception) as e:
            # notify to channel and log it as well
            print("The following error occurred: %s" %
                  e)
            raise

    def invoke_webhook(self, appdata, hook_input_metric, config_file):
        envSet = []
        commandsSet = []
        self.function_execution_start_time = datetime.now()
        self.webhookSetting()
        if (not self.configLoadFlag):
            self.config = self.appconfigObj.getConfig(self.config_dir, config_file)
            self.configLoadFlag = True
            try:
                self.config_channels = Set(self.config['notifications']['channels'])
                self.config_envs = Set(self.config['notifications']['envs'])
                self.config_commands = Set(self.config['notifications']['commands'])
                if (len(self.config_channels) == 0 or len(self.config_envs) == 0 or len(self.config_commands) == 0):
                    return
            except (Exception, KeyError, ValueError) as e:
                # notify to channel and log it as well
                print("The following error occurred: %s" %
                      e)
                raise
        try:
            self.action = self.app_name = self.envr = self.user = ''
            temp = hook_input_metric.split(',')
            for var in temp:
                varAnother = var.split('=')[0]
                if varAnother == 'event':
                    self.action = var.split('=')[1]
                    continue

                if varAnother == 'app_name':
                    self.app_name = var.split('=')[1]
                    continue

                if varAnother == 'env':
                    self.envr = var.split('=')[1]
                    continue

                if varAnother == 'user':
                    self.user = var.split('=')[1]
                    continue
            if len(self.action) == 0 or len(self.app_name) == 0 or len(self.envr) == 0 or len(self.user) == 0:
                raise ValueError

        except (Exception, KeyError, ValueError, IndexError) as e:
            print("The following error occurred: %s" %
                  e)
            raise
        try:
            if 'notifications' in appdata:
                channelsSet = Set(appdata['notifications']['channels'])
                if (len(self.config_channels) != 0):
                    channelsSet = channelsSet.union(self.config_channels)
                envSet = Set(appdata['notifications']['envs'])
                if (len(self.config_channels) != 0):
                    envSet = envSet.union(self.config_envs)
                commandsSet = Set(appdata['notifications']['commands'])
                if (len(self.config_commands) != 0):
                    commandsSet = commandsSet.union(self.config_commands)
                if (len(channelsSet) == 0 or len(envSet) == 0 or len(commandsSet) == 0):
                    return
            else:
                if list(self.config_envs)[0] == 'all':
                    self.config_envs = ['dev', 'production', 'staging', 'local']
                if list(self.config_commands)[0] == 'all':
                    self.config_commands = ['pull', 'build', 'push']
                self.postToSlack(self.action, self.config_envs, self.config_commands, self.config_channels)
                return
            if list(envSet)[0] == 'all':
                envSet = ['dev', 'production', 'staging', 'local']
            if list(commandsSet)[0] == 'all':
                commandsSet = ['pull', 'build', 'push']
        except (Exception, KeyError, ValueError) as e:
            print("The following error occurred: %s" %
                  e)
            raise
        try:
            self.postToSlack(self.action, envSet, commandsSet, channelsSet)
        except (Exception) as e:
            self.custom_api_call("The following error occurred: %s" % e, self.defChannel)
            print("The following error occurred: %s" %
                  e)
            raise

    def postToSlack(self, action, envSet, commandsSet, channelsSet):
        try:
            if ('post' in action and self.envr in envSet and action.split('_')[1] in commandsSet):
                for channel in channelsSet:
                    timeElapsed = '{0:.2f}'.format((datetime.now() - self.function_execution_start_time).total_seconds() * 1000)
                    timeasInt = float(timeElapsed)
                    h, m, s, ms = self.makeTimeReadable(timeasInt)
                    readableTime = self.createMesage(h, m, s, ms)
                    slackMessage = ("Completed *" + action.split('_')[1] + "* of *" + self.app_name + "* on *" + self.envr + "* in *" + readableTime + "*  (triggered by *" + self.user + "*)")
                    self.custom_api_call(slackMessage, '#' + channel)
        except (Exception) as e:
            self.custom_api_call("The following error occurred: %s" % e, self.defChannel)
            print("The following error occurred: %s" %
                  e)
            raise

    def makeTimeReadable(self, ms):
        s = ms / 1000
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        return h, m, s, ms

    def createMesage(self, h, m, s, ms):
        message = ''
        if int(h) > 0:
            message += str(int(h)) + ":hour "
        if int(m) > 0:
            message += str(int(m)) + ":mins "
        if int(s) > 0:
            message += str(int(s)) + ":sec "
        message += str(ms) + ":miliseconds "
        return message
