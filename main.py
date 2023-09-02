

from time import sleep

from command_handler import handle_command, parse_bot_commands
from slack_utils import SLACK_CLIENT


def main():
    if SLACK_CLIENT.rtm_connect(with_team_state=False):
        print("Stack Bot connected and running!")
        while True:
            command, channel = parse_bot_commands(SLACK_CLIENT.rtm_read())
            if command:
                handle_command(command, channel)
            sleep(1)


if __name__ == "__main__":
    main()