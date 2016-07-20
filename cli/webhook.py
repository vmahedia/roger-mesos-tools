import slackweb
from sets import Set
from datetime import datetime

from cli.settings import Settings
from cli.appconfig import AppConfig


class WebHook:

    def __init__(self):
        '''this flag makes sure if initialization fails, many hook
        steps wont try to post message again and again '''
        self.disabled = True
        self.emoji = ':rocket:'
        self.settingObj = Settings()
        self.appconfigObj = AppConfig()

    def webhookSetting(self):
        try:
            config_dir = self.settingObj.getConfigDir()
            roger_env = self.appconfigObj.getRogerEnv(config_dir)
            if 'webhook_url' in roger_env.keys():
                self.webhookURL = roger_env['webhook_url']
            if 'default_channel' in roger_env.keys():
                self.defChannel = roger_env['default_channel']
            if 'default_username' in roger_env.keys():
                self.username = roger_env['default_username']
            if len(self.username) == 0 or len(self.webhookURL) == 0 or len(self.defChannel) == 0:
                return
        except (Exception) as e:
            print("Warning: slackweb basic initialization failed (error: %s).\
            Not using slack." % e)
            return
        try:
            self.client = slackweb.Slack(url=self.webhookURL)
            self.disabled = False
        except (Exception) as e:
            print("Warning: slackweb basic initialization failed (error: %s).\
            Not using slack." % e)
            return  # disabled flag remains False

    def api_call(self, text, channel):
        self.webhookSetting()
        if len(channel) == 0:
            channel = self.defChannel
        if not self.disabled:
            self.client.notify(channel=channel, username=self.username,
                               icon_emoji=self.emoji, text=text)

    def invoke_webhook(self, appdata, hook_input_metric):
        self.webhookSetting()
        message = 'default message'
        envr = 'NA'
        temp = hook_input_metric.split(',')
        """roger-tools.rogeros_tools_exec_time,event=pre_build,app_name=roger-simpleapp,
        identifier=1468986920-bb0d3712,config_name=moz-roger,env=local,user=manish.ranjan'"""

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
        try:
            if 'notifications' in appdata:
                channelsSet = Set(appdata['notifications']['channels'])
                envSet = Set(appdata['notifications']['envs'])
                commandsSet = Set(appdata['notifications']['commands'])
                # to handle no tag at all
                if (len(channelsSet) == 0 or len(envSet) == 0 or len(commandsSet) == 0):
                    print("notificaton tag missing. Aborting message post to slack!")
                    return
            else:
                print("Notificaton tag missing. Aborting message post to slack!")
                return
            # to handle all tag for env and commands
            if list(envSet)[0] == 'all':
                envSet = ['dev', 'production', 'staging', 'local']

            if list(commandsSet)[0] == 'all':
                commandsSet = ['pull', 'build', 'push']
        except (Exception, KeyError, ValueError) as e:
            # notify to channel and log it as well
            self.api_call("The following error occurred: %s" %
                          e, self.defChannel)
            print("The following error occurred: %s" %
                  e)
            raise
        try:
            function_execution_start_time = datetime.now()
            if ('post' in action and envr in envSet and action.split('_')[1] in commandsSet):
                for channel in channelsSet:
                    slackMessage = ("Completed *" + action.split('_')[1] + "* of *" + app_name +
                                    "* on *" + envr + "* in *" +
                                    str((datetime.now() - function_execution_start_time)
                                        .total_seconds() * 1000) +
                                    "* miliseconds (triggered by *" + user + "*)")
                    self.api_call(slackMessage, '#' + channel)
        except (Exception) as e:
            self.api_call("The following error occurred: %s" %
                          e, self.defChannel)
            print("The following error occurred: %s" %
                  e)
            raise
