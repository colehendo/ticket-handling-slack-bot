from os import environ

from flask import make_response
from slackclient import SlackClient


SLACK_BOT_TOKEN = environ["SLACK_BOT_TOKEN"]
SLACK_VERIFICATION_TOKEN = environ["SLACK_VERIFICATION_TOKEN"]

SLACK_CLIENT = SlackClient(SLACK_BOT_TOKEN)

def verify_slack_token(request_token):
    if SLACK_VERIFICATION_TOKEN != request_token:
        print("Error: invalid verification token!")
        print("Received {} but was expecting {}".format(request_token, SLACK_VERIFICATION_TOKEN))
        return make_response("Request contains invalid Slack verification token", 403)
