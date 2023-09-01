from attachment_constants import ACTION_ATTACHMENTS
from slack_utils import SLACK_CLIENT


EXAMPLE_COMMAND = "ticket"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

started = False


def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            starterbot_id = SLACK_CLIENT.api_call("auth.test")["user_id"]
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None


def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)


def handle_command(command, channel):
    global started
    """
        Executes bot command if the command is known
    """

    # Finds and executes the given command, filling in response
    response = "Not sure what you mean. Try *{}*.".format(EXAMPLE_COMMAND)
    if command.startswith(EXAMPLE_COMMAND):
        response = SLACK_CLIENT.api_call(
            "chat.postMessage",
            channel = "SAMPLE-CHANNEL",
            text = "What do you want to do?",
            attachments = ACTION_ATTACHMENTS
        )

    # Sends the response back to the channel
    SLACK_CLIENT.api_call(
        "chat.postMessage",
        channel=channel,
        text=response
    )
    response = None