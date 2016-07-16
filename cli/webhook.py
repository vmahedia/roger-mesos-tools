import sys
import slackweb


class WebHook:

    def __init__(self):
        '''this flag makes sure if initialization fails, many hook
        steps wont try to post message again and again'''
        self.disabled = True
        self.webhookURL = ('https://hooks.slack.com/services/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')
        self.username = 'roger-deploy-bot'
        self.emoji = ':rocket:'
        # default channel unless user overrides
        self.channel = '#testhook'
        try:
            self.client = slackweb.Slack(url=self.webhookURL)
        except (Exception) as e:
            print("Warning: slackweb basic initialization failed (error: %s).\
            Not using slack." % e)
            return  # disabled flag remains False
        self.disabled = False

    def api_call(self, text, channel):
        if not self.disabled:
            self.client.notify(channel=channel, username=self.username,
                               icon_emoji=self.emoji, text=text)
