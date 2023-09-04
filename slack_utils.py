from functools import lru_cache
from os import environ

from flask import make_response
from slackclient import SlackClient


SLACK_BOT_TOKEN = environ["SLACK_BOT_TOKEN"]
SLACK_VERIFICATION_TOKEN = environ["SLACK_VERIFICATION_TOKEN"]

SLACK_CLIENT = SlackClient(SLACK_BOT_TOKEN)


@lru_cache()
def get_starterbot_id():
    starterbot_id = SLACK_CLIENT.api_call("auth.test")["user_id"]
    return starterbot_id



def verify_slack_token(request_token):
    if SLACK_VERIFICATION_TOKEN != request_token:
        print("Error: invalid verification token!")
        print(f"Received {request_token} but was expecting {SLACK_VERIFICATION_TOKEN}")
        return make_response("Request contains invalid Slack verification token", 403)
