import sys
import slackweb
from sets import Set
from datetime import datetime


class WebHook:

    flag = False

    def __init__(self):
        '''this flag makes sure if initialization fails, many hook
        steps wont try to post message again and again'''
        self.disabled = True
        self.webhookURL = ('https://hooks.slack.com/services/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')
        self.username = 'roger-deploy-bot'
        self.emoji = ':rocket:'
        # default channel unless user overrides
        self.defChannel = '#rogeros-deploy'
        try:
            self.client = slackweb.Slack(url=self.webhookURL)
        except (Exception) as e:
            print("Warning: slackweb basic initialization failed (error: %s).\
            Not using slack." % e)
            return  # disabled flag remains False
        self.disabled = False

    def api_call(self, text, channel):
        # this is enable any class to call the method with message and default errorChannel
        if len(channel) == 0:
            channel = self.defChannel
        if not self.disabled:
            self.client.notify(channel=channel, username=self.username,
                               icon_emoji=self.emoji, text=text)

    def invoke_webhook(self, appdata, hook_input_metric):
        # defChannel = '#rogeros-deploy'
        message = 'default message'
        envr = 'NA'
        temp = hook_input_metric.split(',')

        """Default message format:  roger-tools.post_gitpull_time', 'app_name=roger-simpleapp',
        'identifier=1468650484-bb0d3712', 'config_name=moz-roger', 'env=', 'user=manish.ranjan'"""

        for var in temp:
            if 'roger-tools' in var:
                action = ''.join(var.split('.')[1])
                action = '-'.join(action.split('_')[0:2])
                continue

            varAnother = var.split('=')[0]
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
            channelsSet = Set(appdata['notifications']['channels'])
            envSet = Set(appdata['notifications']['envs'])
            commandsSet = Set(appdata['notifications']['commands'])
            # to handle no tag at all
            if (len(channelsSet) == 0 or len(envSet) == 0 or len(commandsSet) == 0):
                message = str('*Switching to defaults*: All environments, all actions')
                # Default message  to slack channel just once
                if self.flag is False:
                    self.api_call(message, self.defChannel)
                channelsSet = [self.defChannel]
                envSet = ['dev', 'production', 'staging', 'local']
                commandsSet = ['pull', 'build', 'push']
                self.flag = True

            # to handle all tag for env and commands
            if list(envSet)[0] == 'all':
                envSet = ['dev', 'production', 'staging', 'local']

            if list(commandsSet)[0] == 'all':
                commandsSet = ['pull', 'build', 'push']

        except (Exception) as e:
            # notify to channel and log it as well
            self.api_call("The following error occurred: %s" %
                          e, self.defChannel)
            print("The following error occurred: %s" %
                  e)
            raise

        try:
            function_execution_start_time = datetime.now()
            if ('post' in action and envr in envSet and action.split('-')[1] in commandsSet):
                for channel in channelsSet:
                    slackMessage = ("Completed *" + action.split('-')[1] + "* of *" + app_name +
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
