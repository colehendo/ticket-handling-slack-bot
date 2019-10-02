from flask import Flask, request, make_response, Response
import os
import json
import time
import re
from slackclient import SlackClient
from slackeventsapi import SlackEventAdapter

# Slack bot user token taken from the environment
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_VERIFICATION_TOKEN = os.environ["SLACK_VERIFICATION_TOKEN"]

# Slack client for Web API requests
slack_client = SlackClient(SLACK_BOT_TOKEN)

# Variables used for listener loop
EXAMPLE_COMMAND = "ticket"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

# Flask localhost webserver for incoming traffic from Slack
app = Flask(__name__)
slack_events_adapter = SlackEventAdapter(SLACK_VERIFICATION_TOKEN, "/slack/events", app)

started = False
done = False

# Variables to store user input
starterbot_id = selection_value = trigger_id = selected_action = selected_stack = selected_from = selected_to = selected_horse = selected_pi = selected_pse = selected_info = None

# Bool variables that dictate the flow of stackbot
make_selection = True
temp_message_ts = ""
code_needed = False
next_button = False
print_next = False
second_next = False
final_print = False
last_buttons = False
print_add = False
edit = False
edit_cau_info = False
edit_cau_info_submit = False

# Helper for verifying that requests came from Slack
def verify_slack_token(request_token):
    if SLACK_VERIFICATION_TOKEN != request_token:
        print("Error: invalid verification token!")
        print("Received {} but was expecting {}".format(request_token, SLACK_VERIFICATION_TOKEN))
        return make_response("Request contains invalid Slack verification token", 403)

def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
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
        response = slack_client.api_call(
            "chat.postMessage",
            channel = "SAMPLE-CHANNEL",
            text = "What do you want to do?",
            attachments = attachments_action
        )

    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response
    )
    response = None


# The endpoint Slack will load your menu options from
@app.route("/slack/message_options", methods=["POST"])
def message_options():
    
    # Parse the request payload
    form_json = json.loads(request.form["payload"])

    # Verify that the request came from Slack
    verify_slack_token(form_json["token"])

    # Dictionary of menu options which will be sent as JSON.
    # This is the initial menu. To add more, copy & paste this and control which one executes through bool variables
    current_options = {
        "options": [
            {
                "text": "Create Stack",
                "value": "Create"
            },
            {
                "text": "Clone Stack",
                "value": "Clone"
            },
            {
                "text": "Upgrade Stack",
                "value": "Upgrade"
            },
            {
                "text": "Clone and Upgrade Stack",
                "value": "Clone and Upgrade"
            },
            {
                "text": "Delete Stack",
                "value": "Delete"
            },
            {
                "text": "Archive Stack",
                "value": "Archive"
            },
            {
                "text": "Unarchive Stack",
                "value": "Unarchive"
            },
            {
                "text": "Other",
                "value": "other"
            }
        ]
    }

    # Load options dict as JSON and respond to Slack
    return Response(json.dumps(current_options), mimetype='application/json')


# The endpoint Slack will send the user's menu selection to
@app.route("/slack/message_actions", methods=["POST"])
def message_actions():
    # This essentially imports the variables from the beginning for use in the function
    global selection_value
    global trigger_id
    global done
    global selected_action
    global selected_stack
    global selected_from
    global selected_to
    global make_selection
    global temp_message_ts
    global code_needed
    global next_button
    global print_next
    global print_final
    global second_next
    global selected_horse
    global selected_hi
    global selected_hse
    global last_buttons
    global selected_info
    global print_add
    global edit
    global edit_cau_info
    global edit_cau_info_submit

    # Parse the request payload. form_json now contains all necessary user information
    form_json = json.loads(request.form["payload"])

    # Verify that the request came from Slack
    verify_slack_token(form_json["token"])

    # This handles any submissions from pop up boxes
    if form_json["type"] == "dialog_submission":

        # This handles submission of the extra info field
        if print_add:
            selected_info = form_json["submission"]["extra_info"]
            if selection_value == "Delete" or selection_value == "Archive" or selection_value == "Unarchive":
                slack_client.api_call(
                    "chat.update",
                    channel = "SAMPLE-CHANNEL",
                    ts = temp_message_ts,
                    text = "*Action:* " + selection_value + " Stack\n*Stack:* " + selected_stack + "\n*Additional Information:* " + selected_info,
                    attachments = attachments_buttons_no_add
                )
            elif selection_value == "Clone":
                slack_client.api_call(
                    "chat.update",
                    channel = "SAMPLE-CHANNEL",
                    ts = temp_message_ts,
                    text = "*Action:* " + selection_value + " Stack\n*Copy stack from:* " + selected_from + "\n*Copy stack to:* " + selected_to + "\n*Additional Information:* " + selected_info,
                    attachments = attachments_buttons_no_add
                )
            elif selection_value == "Clone and Upgrade":
                slack_client.api_call(
                    "chat.update",
                    channel = "SAMPLE-CHANNEL",
                    ts = temp_message_ts,
                    text = "*Action:* " + selection_value + " Stack\n*Copy stack from:* " + selected_from + "\n*Copy stack to:* " + selected_to + "\n*Horse Version:* " + selected_horse + "\n*HI Version:* " + selected_pi + "\n*HSE Version:* " + selected_pse + "\n*Additional Information:* " + selected_info,
                    attachments = attachments_buttons_no_add
                )
            else:
                slack_client.api_call(
                    "chat.update",
                    channel = "SAMPLE-CHANNEL",
                    ts = temp_message_ts,
                    text = "*Action:* " + selection_value + " Stack\n*Stack:* " + selected_stack + "\n*Horse Version:* " + selected_horse + "\n*HI Version:* " + selected_pi + "\n*HSE Version:* " + selected_pse + "\n*Additional Information:* " + selected_info,
                    attachments = attachments_buttons_no_add
                )

        # This executes if the user clicks the edit button
        elif edit:
            # This turns the statement off so that it doesn't accidentally execute
            edit = False
            # This re-records values if they were edited
            if selection_value == "Delete" or selection_value == "Archive" or selection_value == "Unarchive" or selection_value == "Create" or selection_value == "Upgrade":
                selected_stack = form_json["submission"]["edited_stack"]
            if selection_value == "Clone" or selection_value == "Clone and Upgrade":
                selected_from = form_json["submission"]["edited_from"]
                selected_to = form_json["submission"]["edited_to"]
            if selection_value == "Clone and Upgrade" or selection_value == "Upgrade" or selection_value == "Create":
                selected_horse = form_json["submission"]["edited_horse"]
                selected_pi = form_json["submission"]["edited_hi"]
                selected_pse = form_json["submission"]["edited_hse"]
            # This runs if additional information was initially added
            if selected_info != None:
                # This runs because you can only fit 5 fields on one popup.
                # The additional text box is the sixth field for clone and update.
                # Clone and Upgrade is the only one this is applicable for
                # Sends a next button which takes you to the additional information field
                if selection_value == "Clone and Upgrade":
                    edit_cau_info = True
                    slack_client.api_call(
                        "chat.update",
                        channel = "SAMPLE-CHANNEL",
                        ts = temp_message_ts,
                        attachments = attachments_next_button,
                        text = ""
                    )
                # This sends all the buttons out, minus the add button
                else:
                    selected_info = form_json["submission"]["edited_info"]
                    if selection_value == "Delete" or selection_value == "Archive" or selection_value == "Unarchive":
                        slack_client.api_call(
                            "chat.update",
                            channel = "SAMPLE-CHANNEL",
                            ts = temp_message_ts,
                            text = "*Action:* " + selection_value + " Stack\n*Stack:* " + selected_stack + "\n*Additional Information:* " + selected_info,
                            attachments = attachments_buttons_no_add
                            )
                    elif selection_value == "Clone":
                        slack_client.api_call(
                            "chat.update",
                            channel = "SAMPLE-CHANNEL",
                            ts = temp_message_ts,
                            text = "*Action:* " + selection_value + " Stack\n*Copy stack from:* " + selected_from + "\n*Copy stack to:* " + selected_to + "\n*Additional Information:* " + selected_info,
                            attachments = attachments_buttons_no_add
                        )
                    elif selection_value == "Clone and Upgrade":
                        slack_client.api_call(
                            "chat.update",
                            channel = "SAMPLE-CHANNEL",
                            ts = temp_message_ts,
                            text = "*Action:* " + selection_value + " Stack\n*Copy stack from:* " + selected_from + "\n*Copy stack to:* " + selected_to + "\n*Horse Version:* " + selected_horse + "\n*HI Version:* " + selected_pi + "\n*HSE Version:* " + selected_pse + "\n*Additional Information:* " + selected_info,
                            attachments = attachments_buttons_no_add
                        )
                    else:
                        slack_client.api_call(
                            "chat.update",
                            channel = "SAMPLE-CHANNEL",
                            ts = temp_message_ts,
                            text = "*Action:* " + selection_value + " Stack\n*Stack:* " + selected_stack + "\n*Horse Version:* " + selected_horse + "\n*HI Version:* " + selected_pi + "\n*HSE Version:* " + selected_pse + "\n*Additional Information:* " + selected_info,
                            attachments = attachments_buttons_no_add
                        )
            # This sends all the buttons out again
            else:
                if selection_value == "Delete" or selection_value == "Archive" or selection_value == "Unarchive":
                    slack_client.api_call(
                        "chat.update",
                        channel = "SAMPLE-CHANNEL",
                        ts = temp_message_ts,
                        text = "*Action:* " + selection_value + " Stack\n*Stack:* " + selected_stack,
                        attachments = attachments_buttons_add
                    )
                elif selection_value == "Clone":
                    slack_client.api_call(
                        "chat.update",
                        channel = "SAMPLE-CHANNEL",
                        ts = temp_message_ts,
                        text = "*Action:* " + selection_value + " Stack\n*Copy stack from:* " + selected_from + "\n*Copy stack to:* " + selected_to,
                        attachments = attachments_buttons_add
                    )
                elif selection_value == "Clone and Upgrade":
                    slack_client.api_call(
                        "chat.update",
                        channel = "SAMPLE-CHANNEL",
                        ts = temp_message_ts,
                        text = "*Action:* " + selection_value + " Stack\n*Copy stack from:* " + selected_from + "\n*Copy stack to:* " + selected_to + "\n*Horse Version:* " + selected_horse + "\n*HI Version:* " + selected_pi + "\n*HSE Version:* " + selected_pse,
                        attachments = attachments_buttons_add
                    )
                else:
                    slack_client.api_call(
                        "chat.update",
                        channel = "SAMPLE-CHANNEL",
                        ts = temp_message_ts,
                        text = "*Action:* " + selection_value + " Stack\n*Stack:* " + selected_stack + "\n*Horse Version:* " + selected_horse + "\n*HI Version:* " + selected_pi + "\n*HSE Version:* " + selected_pse,
                        attachments = attachments_buttons_add
                    )

        # This records the submission for additional information for Clone and Upgrade
        # then sends out all the buttons minus the add button
        elif edit_cau_info_submit:
            edit_cau_info_submit = False
            selected_info = form_json["submission"]["edited_info"]
            slack_client.api_call(
                "chat.update",
                channel = "SAMPLE-CHANNEL",
                ts = temp_message_ts,
                text = "*Action:* " + selection_value + " Stack\n*Copy stack from:* " + selected_from + "\n*Copy stack to:* " + selected_to + "\n*Horse Version:* " + selected_horse + "\n*HI Version:* " + selected_pi + "\n*HSE Version:* " + selected_pse + "\n*Additional Information:* " + selected_info,
                attachments = attachments_buttons_no_add
            )
                

        # This handles the submission of delete, archive, unarchive and clone first text fields
        elif selection_value == "Delete" or selection_value == "Archive" or selection_value == "Unarchive" or selection_value == "Clone":
            # This stores the values of to and from in clone submission and sends the preview and buttons to slack
            if selection_value == "Clone":
                selected_from = form_json["submission"]["clone_from"]
                selected_to = form_json["submission"]["clone_to"]
                slack_client.api_call(
                    "chat.update",
                    channel = "DB86VU0AX",
                    ts = temp_message_ts,
                    text = "*Action:* " + selection_value + " Stack\n*Copy stack from:* " + selected_from + "\n*Copy stack to:* " + selected_to,
                    attachments = attachments_buttons_add
                )
            # This stores the value of stack name submitted and sends the preview and buttons to slack
            else:
                selected_stack = form_json["submission"]["stack_selection"]
                slack_client.api_call(
                    "chat.update",
                    channel = "SAMPLE-CHANNEL",
                    ts = temp_message_ts,
                    text = "*Action:* " + selection_value + " Stack\n*Stack:* " + selected_stack,
                    attachments = attachments_buttons_add
                )
            # This says we don't need the code versions box
            code_needed = False               
            # This turns on the function that records which button is clicked and sends out following info
            last_buttons = True
        # This is used if the code versions box needs to be opened
        elif code_needed:
            # This records to and from values if clone and upgrade is the initial selection
            if selection_value == "Clone and Upgrade":
                selected_from = form_json["submission"]["clone_from"]
                selected_to = form_json["submission"]["clone_to"]
            # This records submitted stack name if create or upgrade are the initial selections
            else:
                selected_stack = form_json["submission"]["stack_selection"]
            # This makes sure this elif statement is not entered again
            code_needed = False
            # This turns on the function that records that the next button has been clicked and sends out following info
            next_button = True
            # This sends the next button to slack
            slack_client.api_call(
                "chat.update",
                channel = "SAMPLE-CHANNEL",
                ts = temp_message_ts,
                attachments = attachments_next_button,
                text = ""
            )
        # This is the function called after the submission of the code versions box
        elif print_next:
            # This records the values selected in the code versions box in temp variables and then stores those in global variables
            selected_horse = form_json["submission"]["horse_selection"]
            selected_pi = form_json["submission"]["pi_selection"]
            selected_pse = form_json["submission"]["pse_selection"]
            # This executes if any of the selections was specify branch/version...
            if selected_horse == "specify" or selected_pi == "specify" or selected_pse == "specify":
                # This turns on the function that sends the specification text boxes for each selected specify branch/version
                second_next = True
                # This ensures the code versions box won't pop up again
                next_button = False
                # This sends out the second next button
                slack_client.api_call(
                    "chat.update",
                    channel = "SAMPLE-CHANNEL",
                    ts = temp_message_ts,
                    attachments = attachments_next_button,
                    text = ""
                )
            # If no selection was specify branch/version, and the initial selection was clone and upgrade, this executes
            elif selection_value == "Clone and Upgrade":
                # This sends out the add text/finish buttons
                slack_client.api_call(
                    "chat.update",
                    channel = "SAMPLE-CHANNEL",
                    ts = temp_message_ts,
                    text = "*Action:* " + selection_value + " Stack\n*Copy stack from:* " + selected_from + "\n*Copy stack to:* " + selected_to + "\n*horse Version:* " + selected_horse + "\n*PI Version:* " + selected_pi + "\n*PSE Version:* " + selected_pse,
                    attachments = attachments_buttons_add
                )
                # This opens the function that handles the clicking of add text/finish
                last_buttons = True
                # This ensures the code versions box won't pop up again
                next_button = False
            # If no selection was specify branch/version, and the initial selection was create or upgrade, this executes
            else:
                # This sends out the add text/finish buttons
                slack_client.api_call(
                    "chat.update",
                    channel = "SAMPLE-CHANNEL",
                    ts = temp_message_ts,
                    text = "*Action:* " + selection_value + " Stack\n*Stack:* " + selected_stack + "\n*horse Version:* " + selected_horse + "\n*PI Version:* " + selected_pi + "\n*PSE Version:* " + selected_pse,
                    attachments = attachments_buttons_add
                )
                # This opens the function that handles the clicking of add text/finish
                last_buttons = True
                # This ensures the code versions box won't pop up again
                next_button = False
        # This function executes after the submission of the specify branch/version box
        elif print_final:
            # This ensures the specify branch/version box doesn't pop up again
            second_next = False
            # This records the text entry for whichever code versions needed specification
            if selected_horse == "specify":
                selected_horse = form_json["submission"]["horse_spec"]
            if selected_pi == "specify":
                selected_pi = form_json["submission"]["pi_spec"]
            if selected_pse == "specify":
                selected_pse = form_json["submission"]["pse_spec"]
            # This sends out the add text/finish buttons
            if selection_value == "Clone and Upgrade":
                slack_client.api_call(
                    "chat.update",
                    channel = "SAMPLE-CHANNEL",
                    ts = temp_message_ts,
                    text = "*Action:* " + selection_value + " Stack\n*Copy stack from:* " + selected_from + "\n*Copy stack to:* " + selected_to + "\n*horse Version:* " + selected_horse + "\n*PI Version:* " + selected_pi + "\n*PSE Version:* " + selected_pse,
                    attachments = attachments_buttons_add
                )
            else:
                slack_client.api_call(
                    "chat.update",
                    channel = "SAMPLE-CHANNEL",
                    ts = temp_message_ts,
                    text = "*Action:* " + selection_value + " Stack\n*Stack:* " + selected_stack + "\n*horse Version:* " + selected_horse + "\n*PI Version:* " + selected_pi + "\n*PSE Version:* " + selected_pse,
                    attachments = attachments_buttons_add
                )
            # This opens the function that handles the clicking of add text/finish
            last_buttons = True

    # This handles any selection from drop down menus, and any buttons clicked
    if form_json["type"] == "interactive_message":
        # This records the initial menu selection, and then is turned off
        if make_selection:
            selection_value = form_json["actions"][0]["selected_options"][0]["value"]

        # This opens the code versions box if necessary
        if next_button:
            if form_json["actions"][0]["value"] == "quit":
                done = True
                slack_client.api_call(
                    "chat.update",
                    channel = "SAMPLE-CHANNEL",
                    ts = temp_message_ts,
                    attachments = [],
                    text = "Ticket cancelled. Type *@doStack ticket* to start a new one."
                )
            else:
                # This turns on the function that handles the submission of this box
                print_next = True
                temp_message_ts = form_json["message_ts"]
                # This sends out the box
                open_dialog = slack_client.api_call(
                    "dialog.open",
                    trigger_id = form_json["trigger_id"],
                    dialog = {
                        "title": "Enter code versions:",
                        "Submit_label": "Submit",
                        "callback_id": "code_options",
                        "elements": [
                            {
                                "label": "horse:",
                                "type": "select",
                                "name": "horse_selection",
                                "placeholder": "Select a value...",
                                "options": [
                                    {
                                        "label": "Latest Validated",
                                        "value": "Latest Validated"
                                    },
                                    {
                                        "label": "Latest Develop",
                                        "value": "Latest Develop"
                                    },
                                    {
                                        "label": "Whatever is compatible",
                                        "value": "Whatever is compatible"
                                    },
                                    {
                                        "label": "Specify Branch/Version...",
                                        "value": "specify"
                                    }
                                ]
                            },
                            {
                                "label": "PI:",
                                "type": "select",
                                "name": "pi_selection",
                                "placeholder": "Select a value...",
                                "value": "Whatever is compatible",
                                "options": [
                                    {
                                        "label": "Latest Validated",
                                        "value": "Latest Validated"
                                    },
                                    {
                                        "label": "Latest Develop",
                                        "value": "Latest Develop"
                                    },
                                    {
                                        "label": "Whatever is compatible",
                                        "value": "Whatever is compatible"
                                    },
                                    {
                                        "label": "Specify Branch/Version...",
                                        "value": "specify"
                                    }
                                ]
                            },
                            {
                                "label": "PSE:",
                                "type": "select",
                                "name": "pse_selection",
                                "placeholder": "Select a value...",
                                "value": "Whatever is compatible",
                                "options": [
                                    {
                                        "label": "Latest Validated",
                                        "value": "Latest Validated"
                                    },
                                    {
                                        "label": "Latest Develop",
                                        "value": "Latest Develop"
                                    },
                                    {
                                        "label": "Whatever is compatible",
                                        "value": "Whatever is compatible"
                                    },
                                    {
                                        "label": "Specify Branch/Version...",
                                        "value": "specify"
                                    }
                                ]
                            }
                        ]
                    }
                )

        # This sends out the specify branch/version box if necessary
        elif second_next:
            if form_json["actions"][0]["value"] == "quit":
                done = True
                slack_client.api_call(
                    "chat.update",
                    channel = "SAMPLE-CHANNEL",
                    ts = temp_message_ts,
                    attachments = [],
                    text = "Ticket cancelled. Type *@doStack ticket* to start a new one."
                )
            else:
                # This ensures the code version submission handler isn't executed again
                print_next = False
                # This executes the handler for this box
                print_final = True
                temp_message_ts = form_json["message_ts"]
                # The following runs through every possible combination of specification selections
                # It then sends out the box with the necessary text fields that match the selections
                if selected_horse == "specify" and selected_pi == "specify" and selected_pse == "specify":
                    open_dialog = slack_client.api_call(
                        "dialog.open",
                        trigger_id = form_json["trigger_id"],
                        dialog = {
                            "title": "Specify Branch/Version:",
                            "Submit_label": "Submit",
                            "callback_id": "code_options",
                            "elements": [
                                {
                                    "label": "Specify horse:",
                                    "type": "text",
                                    "name": "horse_spec",
                                    "placeholder": "Specify Horse here"
                                },
                                {
                                    "label": "Specify PI:",
                                    "type": "text",
                                    "name": "pi_spec",
                                    "placeholder": "Specify PI here"
                                },
                                {
                                    "label": "Specify PSE:",
                                    "type": "text",
                                    "name": "pse_spec",
                                    "placeholder": "Specify PSE here"
                                }
                            ]
                        }
                    )
                elif selected_horse == "specify" and selected_pi == "specify":
                    open_dialog = slack_client.api_call(
                        "dialog.open",
                        trigger_id = form_json["trigger_id"],
                        dialog = {
                            "title": "Specify Branch/Version:",
                            "Submit_label": "Submit",
                            "callback_id": "code_options",
                            "elements": [
                                {
                                    "label": "Specify Horse:",
                                    "type": "text",
                                    "name": "horse_spec",
                                    "placeholder": "Specify Horse here"
                                },
                                {
                                    "label": "Specify PI:",
                                    "type": "text",
                                    "name": "pi_spec",
                                    "placeholder": "Specify PI here"
                                }
                            ]
                        }
                    )
                elif selected_horse == "specify" and selected_pse == "specify":
                    open_dialog = slack_client.api_call(
                        "dialog.open",
                        trigger_id = form_json["trigger_id"],
                        dialog = {
                            "title": "Specify Branch/Version:",
                            "Submit_label": "Submit",
                            "callback_id": "code_options",
                            "elements": [
                                {
                                    "label": "Specify Horse:",
                                    "type": "text",
                                    "name": "horse_spec",
                                    "placeholder": "Specify Horse here"
                                },
                                {
                                    "label": "Specify PSE:",
                                    "type": "text",
                                    "name": "pse_spec",
                                    "placeholder": "Specify PSE here"
                                },
                            ]
                        }
                    )
                elif selected_pi == "specify" and selected_pse == "specify":
                    open_dialog = slack_client.api_call(
                        "dialog.open",
                        trigger_id = form_json["trigger_id"],
                        dialog = {
                            "title": "Specify Branch/Version:",
                            "Submit_label": "Submit",
                            "callback_id": "code_options",
                            "elements": [
                                {
                                    "label": "Specify PI:",
                                    "type": "text",
                                    "name": "pi_spec",
                                    "placeholder": "Specify PI here"
                                },
                                {
                                    "label": "Specify PSE:",
                                    "type": "text",
                                    "name": "pse_spec",
                                    "placeholder": "Specify PSE here"
                                }
                            ]
                        }
                    )
                elif selected_horse == "specify":
                    open_dialog = slack_client.api_call(
                        "dialog.open",
                        trigger_id = form_json["trigger_id"],
                        dialog = {
                            "title": "Specify Branch/Version:",
                            "Submit_label": "Submit",
                            "callback_id": "code_options",
                            "elements": [
                                {
                                    "label": "Specify Horse:",
                                    "type": "text",
                                    "name": "horse_spec",
                                    "placeholder": "Specify Horse here"
                                }
                            ]
                        }
                    )
                elif selected_pi == "specify":
                    open_dialog = slack_client.api_call(
                        "dialog.open",
                        trigger_id = form_json["trigger_id"],
                        dialog = {
                            "title": "Specify Branch/Version:",
                            "Submit_label": "Submit",
                            "callback_id": "code_options",
                            "elements": [
                                {
                                    "label": "Specify PI:",
                                    "type": "text",
                                    "name": "pi_spec",
                                    "placeholder": "Specify PI here"
                                }
                            ]
                        }
                    )
                elif selected_pse == "specify":
                    open_dialog = slack_client.api_call(
                        "dialog.open",
                        trigger_id = form_json["trigger_id"],
                        dialog = {
                            "title": "Specify Branch/Version:",
                            "Submit_label": "Submit",
                            "callback_id": "code_options",
                            "elements": [
                                {
                                    "label": "Specify PSE:",
                                    "type": "text",
                                    "name": "pse_spec",
                                    "placeholder": "Specify PSE here"
                                }
                            ]
                        }
                    )
                # A very basic error handler just incase. Sends ERROR to the command line
                else:
                    print("ERROR")

        # This sends out the additional information box for Clone and Upgrade
        # if edit is selected
        elif edit_cau_info:
            edit = False
            edit_cau_info = False
            if form_json["actions"][0]["value"] == "quit":
                done = True
                slack_client.api_call(
                    "chat.update",
                    channel = "SAMPLE-CHANNEL",
                    ts = temp_message_ts,
                    attachments = [],
                    text = "Ticket cancelled. Type *@doStack ticket* to start a new one."
                )
            else:
                edit_cau_info_submit = True
                open_dialog = slack_client.api_call(
                    "dialog.open",
                    trigger_id = form_json["trigger_id"],
                    dialog = {
                        "title": selection_value + " Stack",
                        "Submit_label": "Submit",
                        "callback_id": "code_options",
                        "elements": [
                            {
                                "label": "Additional Information",
                                "type": "text",
                                "optional": "true",
                                "name": "edited_info",
                                "value": selected_info
                            }
                        ]
                    }
                )

        # This handles the clicking of buttons finish, add text, and cancel
        elif last_buttons:
            # This executes if the edit button is selected
            if form_json["actions"][0]["value"] == "edit":
                print_add = False
                edit = True
                # This executes if the add text button was never clicked/no extra info has been added
                if selected_info == None:
                    # The following prints a box with the previously submitted text fields
                    # based on your initial selection
                    if selection_value == "Delete" or selection_value == "Archive" or selection_value == "Unarchive":
                        open_dialog = slack_client.api_call(
                            "dialog.open",
                            trigger_id = form_json["trigger_id"],
                            dialog = {
                                "title": selection_value + " Stack",
                                "Submit_label": "Submit",
                                "callback_id": "edit_first_no_add",
                                "elements": [
                                    {
                                        "label": "Stack to " + selection_value,
                                        "type": "text",
                                        "name": "edited_stack",
                                        "value": selected_stack
                                    }
                                ]
                            }
                        )
                    elif selection_value == "Clone":
                        open_dialog = slack_client.api_call(
                            "dialog.open",
                            trigger_id = form_json["trigger_id"],
                            dialog = {
                                "title": selection_value + " Stack",
                                "Submit_label": "Submit",
                                "callback_id": "edit_clone_no_add",
                                "elements": [
                                    {
                                        "label": "From",
                                        "type": "text",
                                        "name": "edited_from",
                                        "value": selected_from
                                    },
                                    {
                                        "label": "To",
                                        "type": "text",
                                        "name": "edited_to",
                                        "value": selected_to
                                    }
                                ]
                            }
                        )
                    elif selection_value == "Clone and Upgrade":
                        open_dialog = slack_client.api_call(
                            "dialog.open",
                            trigger_id = form_json["trigger_id"],
                            dialog = {
                                "title": selection_value + " Stack",
                                "Submit_label": "Submit",
                                "callback_id": "edit_clone_and_upgrade_no_add",
                                "elements": [
                                    {
                                        "label": "From",
                                        "type": "text",
                                        "name": "edited_from",
                                        "value": selected_from
                                    },
                                    {
                                        "label": "To",
                                        "type": "text",
                                        "name": "edited_to",
                                        "value": selected_to
                                    },
                                    {
                                        "label": "horse Version",
                                        "type": "text",
                                        "name": "edited_horse",
                                        "value": selected_horse
                                    },
                                    {
                                        "label": "PI Version",
                                        "type": "text",
                                        "name": "edited_pi",
                                        "value": selected_pi
                                    },
                                    {
                                        "label": "PSE Version",
                                        "type": "text",
                                        "name": "edited_pse",
                                        "value": selected_pse
                                    }
                                ]
                            }
                        )
                    else:
                        open_dialog = slack_client.api_call(
                            "dialog.open",
                            trigger_id = form_json["trigger_id"],
                            dialog = {
                                "title": selection_value + " Stack",
                                "Submit_label": "Submit",
                                "callback_id": "edit_clone_and_upgrade_no_add",
                                "elements": [
                                    {
                                        "label": "Stack to " + selection_value,
                                        "type": "text",
                                        "name": "edited_stack",
                                        "value": selected_stack
                                    },
                                    {
                                        "label": "Horse Version",
                                        "type": "text",
                                        "name": "edited_horse",
                                        "value": selected_horse
                                    },
                                    {
                                        "label": "PI Version",
                                        "type": "text",
                                        "name": "edited_pi",
                                        "value": selected_pi
                                    },
                                    {
                                        "label": "PSE Version",
                                        "type": "text",
                                        "name": "edited_pse",
                                        "value": selected_pse
                                    }
                                ]
                            }
                        )
                # This executes if the add text button was  clicked/extra info has been added
                else:
                    # The following prints a box with the previously submitted text fields and the additional info field
                    # based on your initial selection
                    if selection_value == "Delete" or selection_value == "Archive" or selection_value == "Unarchive":
                        open_dialog = slack_client.api_call(
                            "dialog.open",
                            trigger_id = form_json["trigger_id"],
                            dialog = {
                                "title": selection_value + " Stack",
                                "Submit_label": "Submit",
                                "callback_id": "edit_first_no_add",
                                "elements": [
                                    {
                                        "label": "Stack to " + selection_value,
                                        "type": "text",
                                        "name": "edited_stack",
                                        "value": selected_stack
                                    },
                                    {
                                        "label": "Additional Information",
                                        "type": "text",
                                        "optional": "true",
                                        "name": "edited_info",
                                        "value": selected_info
                                    }
                                ]
                            }
                        )
                    elif selection_value == "Clone":
                        open_dialog = slack_client.api_call(
                            "dialog.open",
                            trigger_id = form_json["trigger_id"],
                            dialog = {
                                "title": selection_value + " Stack",
                                "Submit_label": "Submit",
                                "callback_id": "edit_clone_no_add",
                                "elements": [
                                    {
                                        "label": "From",
                                        "type": "text",
                                        "name": "edited_from",
                                        "value": selected_from
                                    },
                                    {
                                        "label": "To",
                                        "type": "text",
                                        "name": "edited_to",
                                        "value": selected_to
                                    },
                                    {
                                        "label": "Additional Information",
                                        "type": "text",
                                        "optional": "true",
                                        "name": "edited_info",
                                        "value": selected_info
                                    }
                                ]
                            }
                        )
                    elif selection_value == "Clone and Upgrade":
                        open_dialog = slack_client.api_call(
                            "dialog.open",
                            trigger_id = form_json["trigger_id"],
                            dialog = {
                                "title": selection_value + " Stack",
                                "Submit_label": "Submit",
                                "callback_id": "edit_clone_and_upgrade_no_add",
                                "elements": [
                                    {
                                        "label": "From",
                                        "type": "text",
                                        "name": "edited_from",
                                        "value": selected_from
                                    },
                                    {
                                        "label": "To",
                                        "type": "text",
                                        "name": "edited_to",
                                        "value": selected_to
                                    },
                                    {
                                        "label": "Horse Version",
                                        "type": "text",
                                        "name": "edited_horse",
                                        "value": selected_horse
                                    },
                                    {
                                        "label": "PI Version",
                                        "type": "text",
                                        "name": "edited_pi",
                                        "value": selected_pi
                                    },
                                    {
                                        "label": "PSE Version",
                                        "type": "text",
                                        "name": "edited_pse",
                                        "value": selected_pse
                                    },
                                ]
                            }
                        )
                    else:
                        open_dialog = slack_client.api_call(
                            "dialog.open",
                            trigger_id = form_json["trigger_id"],
                            dialog = {
                                "title": selection_value + " Stack",
                                "Submit_label": "Submit",
                                "callback_id": "edit_clone_and_upgrade_no_add",
                                "elements": [
                                    {
                                        "label": "Stack to " + selection_value,
                                        "type": "text",
                                        "name": "edited_stack",
                                        "value": selected_stack
                                    },
                                    {
                                        "label": "Horse Version",
                                        "type": "text",
                                        "name": "edited_horse",
                                        "value": selected_horse
                                    },
                                    {
                                        "label": "PI Version",
                                        "type": "text",
                                        "name": "edited_pi",
                                        "value": selected_pi
                                    },
                                    {
                                        "label": "PSE Version",
                                        "type": "text",
                                        "name": "edited_pse",
                                        "value": selected_pse
                                    },
                                    {
                                        "label": "Additional Information",
                                        "type": "text",
                                        "optional": "true",
                                        "name": "edited_info",
                                        "value": selected_info
                                    }
                                ]
                            }
                        )
            
            # This handles the clicking of finish button 
            elif form_json["actions"][0]["value"] == "finish":
                # This executes if the add text button was never clicked/no extra info has been added
                if selected_info == None:
                    # The following prints the jirio command based on your initial selection
                    if selection_value == "Delete" or selection_value == "Archive" or selection_value == "Unarchive":
                        slack_client.api_call(
                            "chat.update",
                            channel = "SAMPLE-CHANNEL",
                            ts = temp_message_ts,
                            attachments = [],
                            text = ":checkered_flag: Please copy and paste the following into <#C0UJWRKHU>:\n`/jirio create task " + selection_value + " " + selected_stack + "`"
                        )
                    elif selection_value == "Clone":
                        slack_client.api_call(
                            "chat.update",
                            channel = "SAMPLE-CHANNEL",
                            ts = temp_message_ts,
                            attachments = [],
                            text = ":checkered_flag: Please copy and paste the following into <#C0UJWRKHU>:\n`/jirio create task " + selection_value + " Stack from " + selected_from + " to " + selected_to + "`"
                        )
                    elif selection_value == "Clone and Upgrade":
                        slack_client.api_call(
                            "chat.update",
                            channel = "SAMPLE-CHANNEL",
                            ts = temp_message_ts,
                            attachments = [],
                            text = ":checkered_flag: Please copy and paste the following into <#C0UJWRKHU>:\n`/jirio create task " + selection_value + " Stack from " + selected_from + " to " + selected_to + ". Horse: " + selected_horse + " -- PI: " + selected_pi + " -- PSE: " + selected_pse + "`"
                        )
                    else:
                        slack_client.api_call(
                            "chat.update",
                            channel = "SAMPLE-CHANNEL",
                            ts = temp_message_ts,
                            attachments = [],
                            text = ":checkered_flag: Please copy and paste the following into <#C0UJWRKHU>:\n`/jirio create task " + selection_value + " Stack " + selected_stack + " -- Horse: " + selected_horse + " -- PI: " + selected_pi + " -- PSE: " + selected_pse + "`"
                        )
                # This executes if the add text button was  clicked/extra info has been added
                else:
                    # The following prints the jirio command based on your initial selection plus the extra info
                    if selection_value == "Delete" or selection_value == "Archive" or selection_value == "Unarchive":
                        slack_client.api_call(
                            "chat.update",
                            channel = "SAMPLE-CHANNEL",
                            ts = temp_message_ts,
                            attachments = [],
                            text = ":checkered_flag: Please copy and paste the following into <#C0UJWRKHU>:\n`/jirio create task " + selection_value + " " + selected_stack + ". " + selected_info + "`"
                        )
                    elif selection_value == "Clone":
                        slack_client.api_call(
                            "chat.update",
                            channel = "SAMPLE-CHANNEL",
                            ts = temp_message_ts,
                            attachments = [],
                            text = ":checkered_flag: Please copy and paste the following into <#C0UJWRKHU>:\n`/jirio create task " + selection_value + " Stack from " + selected_from + " to " + selected_to + ". " + selected_info + "`"
                        )
                    elif selection_value == "Clone and Upgrade":
                        slack_client.api_call(
                            "chat.update",
                            channel = "SAMPLE-CHANNEL",
                            ts = temp_message_ts,
                            attachments = [],
                            text = ":checkered_flag: Please copy and paste the following into <#C0UJWRKHU>:\n`/jirio create task " + selection_value + " Stack from " + selected_from + " to " + selected_to + ". Horse: " + selected_horse + " -- PI: " + selected_pi + " -- PSE: " + selected_pse + ". " + selected_info + "`"
                        )
                    else:
                        slack_client.api_call(
                            "chat.update",
                            channel = "SAMPLE-CHANNEL",
                            ts = temp_message_ts,
                            attachments = [],
                            text = ":checkered_flag: Please copy and paste the following into <#C0UJWRKHU>:\n`/jirio create task " + selection_value + " Stack " + selected_stack + " -- Horse: " + selected_horse + " -- PI: " + selected_pi + " -- PSE: " + selected_pse + ". " + selected_info + "`"
                        )
                # This opens the statement that starts the listener, essentially looping the bot after printing the ticket
                done = True
                
            # This handles the clicking of add button 
            elif form_json["actions"][0]["value"] == "add":
                # This enables the function that handles the submitted extra text
                print_add = True
                # This sends out the additional info text box
                open_dialog = slack_client.api_call(
                    "dialog.open",
                    trigger_id = form_json["trigger_id"],
                    dialog = {
                        "title": "Additional Information",
                        "Submit_label": "Submit",
                        "callback_id": "extra_info",
                        "elements": [
                            {
                                "label": "Enter text here:",
                                "type": "text",
                                "name": "extra_info",
                                "placeholder": "Provide additional information",
                                "hint": "Any additional information DevOps may need to complete this ticket in a timely fashion."
                            }
                        ]
                    }
                )

            # This handles the clicking of cancel button
            elif form_json["actions"][0]["value"] == "quit":
                # This restarts the ticket
                done = True
                # This sends a quit message out
                slack_client.api_call(
                    "chat.update",
                    channel = "SAMPLE-CHANNEL",
                    ts = temp_message_ts,
                    attachments = [],
                    text = "Ticket cancelled. Type *@doStack ticket* to start a new one."
                )

            else:
                print("ERROR")

        # This is the handler for the selection other
        elif selection_value == "other":
            # This enables the reset listener loop
            done = True
            # This sends out the other error message
            slack_client.api_call(
                "chat.update",
                channel = "SAMPLE-CHANNEL",
                ts = form_json["message_ts"],
                attachments = [],
                text = "I'm sorry, currently those are the only options.\nPlease write a ticket using jirio in the <#SAMPLE-CHANNEL> channel."
            )

        # This handles initial selections of create, upgrade, delete, archive, and unarchive
        # It is important that this is near the bottom as selection_values are one of the first variables and do not change,
        # therefore the above functions would not execute if this was at the top, and this would just continually execute
        elif selection_value == "Create" or selection_value == "Upgrade" or selection_value == "Delete" or selection_value == "Archive" or selection_value == "Unarchive":
            code_needed = True
            make_selection = False
            temp_message_ts = form_json["message_ts"]
            open_dialog = slack_client.api_call(
                "dialog.open",
                trigger_id = form_json["trigger_id"],
                dialog = {
                    "title": "Stack to " + selection_value + ":",
                    "submit_label": "Submit",
                    "callback_id": "stack_options",
                    "elements": [
                        {
                            "label": "Name must be lowercase.",
                            "type": "text",
                            "name": "stack_selection",
                        }
                    ]
                }
            )
        # This handles initial selections of clone, and clone and upgrade
        # It is important that this is near the bottom for the same reason as above
        else:
            code_needed = True
            make_selection = False
            temp_message_ts = form_json["message_ts"]
            open_dialog = slack_client.api_call(
                "dialog.open",
                trigger_id = form_json["trigger_id"],
                dialog = {
                    "title": "I want to clone",
                    "submit_label": "Submit",
                    "callback_id": "clone_options",
                    "elements": [
                        {
                            "label": "From:",
                            "type": "text",
                            "name": "clone_from",
                        },
                        {
                            "label": "To:",
                            "type": "text",
                            "name": "clone_to",
                        }
                    ]
                }
            )

    # This function starts the listener again, and resets the variables
    if done:
        # The following line was in the original code, but broke the new code. Leave just incase
        # if slack_client.rtm_connect(with_team_state=False):
        # The following bullions reset all the variables of the bot in order to restart it
        done = False
        make_selection = True
        selection_value = selected_horse = selected_pi = selected_pse = selected_info = None
        code_needed = False
        next_button = False
        print_next = False
        second_next = False
        final_print = False
        last_buttons = False
        print_add = False
        # This prints to the commandline as a test to make sure it is running
        print("Stack Bot connected and running!")
            # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        # This loop sits and listens for @stackbot ticket to be sent
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel)
            time.sleep(1)
                
    # Send an HTTP 200 response with empty body so Slack knows we're done here
    return make_response("", 200)

# A Dictionary of initial message options
attachments_action = [
    {
        "fallback": "Upgrade your Slack client to use messages like these.",
        "color": "#228B22",
        "attachment_type": "default",
        "callback_id": "attachments_action",
        "actions": [
            {
                "name": "pick_action",
                "text": "Pick an action...",
                "type": "select",
                "data_source": "external"
            }
        ]
    }
]

# The attachment for the next button
attachments_next_button = [
    {
        "fallback": "Upgrade your Slack client to use messages like these.",
        "color": "#228B22",
        "attachment_type": "default",
        "callback_id": "attachments_next",
        "actions": [
            {
                "name": "first_list",
                "text": "Next",
                "style": "primary",
                "type": "button",
                "value": "next"
            },
            {
                "name": "first_list",
                "text": "Quit",
                "style": "danger",
                "type": "button",
                "value": "quit"
            }
        ]
    }
]

# The attachment for edit, finish, and cancel buttons
attachments_buttons_no_add = [
    {
        "fallback": "Upgrade your Slack client to use messages like these.",
        "text": "If this looks correct, click *Finish* to generate your ticket. Otherwise, click *Edit*, or *Cancel* to start over.",
        "color": "#228B22",
        "attachment_type": "default",
        "callback_id": "double_button",
        "actions": [
            {
                "name": "edit_button",
                "text": "Edit",
                "type": "button",
                "value": "edit"
            },
            {
                "name": "finish_button",
                "text": "Finish",
                "style": "primary",
                "type": "button",
                "value": "finish"
            },
            {
                "name": "cancel_button",
                "text": "Quit",
                "style": "danger",
                "type": "button",
                "value": "quit"
            }
        ]
    }
]

# The attachment for all buttons minus the preview button
attachments_buttons_add = [
    {
        "fallback": "Upgrade your Slack client to use messages like these.",
        "text": "If this looks correct, click *Finish* to generate your ticket. Otherwise, click *Edit*, or *Cancel* to start over.\nTo add additional information, click *Add Text*.",
        "color": "#228B22",
        "attachment_type": "default",
        "callback_id": "double_button",
        "actions": [
            {
                "name": "add_text",
                "text": "Add Text",
                "type": "button",
                "value": "add"
            },
            {
                "name": "edit_button",
                "text": "Edit",
                "type": "button",
                "value": "edit"
            },
            {
                "name": "finish_button",
                "text": "Finish",
                "style": "primary",
                "type": "button",
                "value": "finish"
            },
            {
                "name": "cancel_button",
                "text": "Quit",
                "style": "danger",
                "type": "button",
                "value": "quit"
            }
        ]
    }
]

# This is the initial listener when the file is run
if slack_client.rtm_connect(with_team_state=False):
    print("Stack Bot connected and running!")
    # Read bot's user ID by calling Web API method `auth.test`
    starterbot_id = slack_client.api_call("auth.test")["user_id"]
    while True:
        command, channel = parse_bot_commands(slack_client.rtm_read())
        if command:
            handle_command(command, channel)
        time.sleep(1)
