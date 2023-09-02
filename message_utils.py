import json

from flask import Flask, request, make_response, Response
from time import sleep

from constants import ACTION_OPTIONS, BUTTON_ATTACHMENTS_NO_TEXT_ADDED, BUTTON_ATTACHMENTS_NO_TEXT_ADDED, NEXT_BUTTON_ATTACHMENTS
from command_handler import handle_command, parse_bot_commands
from slack_utils import SLACK_CLIENT, verify_slack_token


app = Flask(__name__)

selection_value = trigger_id = selected_action = selected_stack = selected_from = selected_to = selected_horse = selected_pi = selected_pse = selected_info = None

done = False
make_selection = True
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


@app.route("/slack/message_options", methods=["POST"])
def message_options():
    form_json = json.loads(request.form["payload"])
    verify_slack_token(form_json["token"])
    return Response(json.dumps(ACTION_OPTIONS), mimetype='application/json')


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
    global code_needed
    global next_button
    global print_next
    global second_next
    global selected_horse
    global last_buttons
    global selected_info
    global print_add
    global edit
    global edit_cau_info
    global edit_cau_info_submit

    form_json = json.loads(request.form["payload"])

    verify_slack_token(form_json["token"])

    form_type = form_json.get("type")

    

    # This handles any submissions from pop up boxes
    if form_type == "dialog_submission":
        handle_dialog_submission(form_json["submission"])


    # This handles any selection from drop down menus, and any buttons clicked
    elif form_type == "interactive_message":
        handle_interactive_message(form_json)
        

    # This function starts the listener again, and resets the variables
    if done:
        # The following line was in the original code, but broke the new code. Leave just incase
        # if SLACK_CLIENT.rtm_connect(with_team_state=False):
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
        starterbot_id = SLACK_CLIENT.api_call("auth.test")["user_id"]
        # This loop sits and listens for @stackbot ticket to be sent
        while True:
            command, channel = parse_bot_commands(SLACK_CLIENT.rtm_read(), starterbot_id)
            if command:
                handle_command(command, channel)
            sleep(1)
                
    # Send an HTTP 200 response with empty body so Slack knows we're done here
    return make_response("", 200)


def handle_dialog_submission(submission):
    attachments = None
    text = ""

    if print_add:
        attachments = BUTTON_ATTACHMENTS_NO_TEXT_ADDED
        selected_info = submission["extra_info"]
        if selection_value == "Delete" or selection_value == "Archive" or selection_value == "Unarchive":
            text = f"*Action:* {selection_value} Stack\n*Stack:* {selected_stack}\n*Additional Information:* {selected_info}",
        elif selection_value == "Clone":
            text = f"*Action:* {selection_value} Stack\n*Copy stack from:* {selected_from}\n*Copy stack to:* {selected_to}\n*Additional Information:* {selected_info}",
        elif selection_value == "Clone and Upgrade":
            text = f"*Action:* {selection_value} Stack\n*Copy stack from:* {selected_from}\n*Copy stack to:* {selected_to}\n*Horse Version:* {selected_horse}\n*HI Version:* {selected_pi}\n*HSE Version:* {selected_pse}\n*Additional Information:* {selected_info}",
        else:
            text = f"*Action:* {selection_value} Stack\n*Stack:* {selected_stack}\n*Horse Version:* {selected_horse}\n*HI Version:* {selected_pi}\n*HSE Version:* {selected_pse}\n*Additional Information:* {selected_info}",

    # This executes if the user clicks the edit button
    elif edit:
        # This turns the statement off so that it doesn't accidentally execute
        edit = False
        # This re-records values if they were edited
        if selection_value == "Delete" or selection_value == "Archive" or selection_value == "Unarchive" or selection_value == "Create" or selection_value == "Upgrade":
            selected_stack = submission["edited_stack"]
        if selection_value == "Clone" or selection_value == "Clone and Upgrade":
            selected_from = submission["edited_from"]
            selected_to = submission["edited_to"]
        if selection_value == "Clone and Upgrade" or selection_value == "Upgrade" or selection_value == "Create":
            selected_horse = submission["edited_horse"]
            selected_pi = submission["edited_hi"]
            selected_pse = submission["edited_hse"]
        # This runs if additional information was initially added
        if selected_info != None:
            # This runs because you can only fit 5 fields on one popup.
            # The additional text box is the sixth field for clone and update.
            # Clone and Upgrade is the only one this is applicable for
            # Sends a next button which takes you to the additional information field
            if selection_value == "Clone and Upgrade":
                edit_cau_info = True
                attachments = NEXT_BUTTON_ATTACHMENTS,
            # This sends all the buttons out, minus the add button
            else:
                attachments = BUTTON_ATTACHMENTS_NO_TEXT_ADDED
                selected_info = submission["edited_info"]
                if selection_value == "Delete" or selection_value == "Archive" or selection_value == "Unarchive":
                    text = f"*Action:* {selection_value} Stack\n*Stack:* {selected_stack}\n*Additional Information:* {selected_info}",
                elif selection_value == "Clone":
                    text = f"*Action:* {selection_value} Stack\n*Copy stack from:* {selected_from}\n*Copy stack to:* {selected_to}\n*Additional Information:* {selected_info}",
                elif selection_value == "Clone and Upgrade":
                    text = f"*Action:* {selection_value} Stack\n*Copy stack from:* {selected_from}\n*Copy stack to:* {selected_to}\n*Horse Version:* {selected_horse}\n*HI Version:* {selected_pi}\n*HSE Version:* {selected_pse}\n*Additional Information:* {selected_info}",
                else:
                    text = f"*Action:* {selection_value} Stack\n*Stack:* {selected_stack}\n*Horse Version:* {selected_horse}\n*HI Version:* {selected_pi}\n*HSE Version:* {selected_pse}\n*Additional Information:* {selected_info}",
        # This sends all the buttons out again
        else:
            attachments = BUTTON_ATTACHMENTS_NO_TEXT_ADDED
            if selection_value == "Delete" or selection_value == "Archive" or selection_value == "Unarchive":
                text = f"*Action:* {selection_value} Stack\n*Stack:* {selected_stack}",

            elif selection_value == "Clone":
                text = f"*Action:* {selection_value} Stack\n*Copy stack from:* {selected_from}\n*Copy stack to:* {selected_to}",
            elif selection_value == "Clone and Upgrade":
                text = f"*Action:* {selection_value} Stack\n*Copy stack from:* {selected_from}\n*Copy stack to:* {selected_to}\n*Horse Version:* {selected_horse}\n*HI Version:* {selected_pi}\n*HSE Version:* {selected_pse}",

            else:
                text = f"*Action:* {selection_value} Stack\n*Stack:* {selected_stack}\n*Horse Version:* {selected_horse}\n*HI Version:* {selected_pi}\n*HSE Version:* {selected_pse}",

    # This records the submission for additional information for Clone and Upgrade
    # then sends out all the buttons minus the add button
    elif edit_cau_info_submit:
        edit_cau_info_submit = False
        selected_info = submission["edited_info"]
        text = f"*Action:* {selection_value} Stack\n*Copy stack from:* {selected_from}\n*Copy stack to:* {selected_to}\n*Horse Version:* {selected_horse}\n*HI Version:* {selected_pi}\n*HSE Version:* {selected_pse}\n*Additional Information:* {selected_info}",
        attachments = BUTTON_ATTACHMENTS_NO_TEXT_ADDED

    # This handles the submission of delete, archive, unarchive and clone first text fields
    elif selection_value == "Delete" or selection_value == "Archive" or selection_value == "Unarchive" or selection_value == "Clone":
        # This stores the values of to and from in clone submission and sends the preview and buttons to slack
        if selection_value == "Clone":
            selected_from = submission["clone_from"]
            selected_to = submission["clone_to"]
            text = f"*Action:* {selection_value} Stack\n*Copy stack from:* {selected_from}\n*Copy stack to:* {selected_to}",
            attachments = BUTTON_ATTACHMENTS_NO_TEXT_ADDED
        # This stores the value of stack name submitted and sends the preview and buttons to slack
        else:
            selected_stack = submission["stack_selection"]
            text = f"*Action:* {selection_value} Stack\n*Stack:* {selected_stack}",
            attachments = BUTTON_ATTACHMENTS_NO_TEXT_ADDED
        # This says we don't need the code versions box
        code_needed = False               
        # This turns on the function that records which button is clicked and sends out following info
        last_buttons = True
    # This is used if the code versions box needs to be opened
    elif code_needed:
        # This records to and from values if clone and upgrade is the initial selection
        if selection_value == "Clone and Upgrade":
            selected_from = submission["clone_from"]
            selected_to = submission["clone_to"]
        # This records submitted stack name if create or upgrade are the initial selections
        else:
            selected_stack = submission["stack_selection"]
        # This makes sure this elif statement is not entered again
        code_needed = False
        # This turns on the function that records that the next button has been clicked and sends out following info
        next_button = True
        # This sends the next button to slack
        attachments = NEXT_BUTTON_ATTACHMENTS,
        text = ""
    # This is the function called after the submission of the code versions box
    elif print_next:
        # This records the values selected in the code versions box in temp variables and then stores those in global variables
        selected_horse = submission["horse_selection"]
        selected_pi = submission["pi_selection"]
        selected_pse = submission["pse_selection"]
        # This executes if any of the selections was specify branch/version...
        if selected_horse == "specify" or selected_pi == "specify" or selected_pse == "specify":
            # This turns on the function that sends the specification text boxes for each selected specify branch/version
            second_next = True
            # This ensures the code versions box won't pop up again
            next_button = False
            # This sends out the second next button
            attachments = NEXT_BUTTON_ATTACHMENTS,
            text = ""
        # If no selection was specify branch/version, and the initial selection was clone and upgrade, this executes
        elif selection_value == "Clone and Upgrade":
            # This sends out the add text/finish buttons
            text = f"*Action:* {selection_value} Stack\n*Copy stack from:* {selected_from}\n*Copy stack to:* {selected_to}\n*horse Version:* {selected_horse}\n*PI Version:* {selected_pi}\n*PSE Version:* {selected_pse}",
            attachments = BUTTON_ATTACHMENTS_NO_TEXT_ADDED
            # This opens the function that handles the clicking of add text/finish
            last_buttons = True
            # This ensures the code versions box won't pop up again
            next_button = False
        # If no selection was specify branch/version, and the initial selection was create or upgrade, this executes
        else:
            # This sends out the add text/finish buttons
            text = f"*Action:* {selection_value} Stack\n*Stack:* {selected_stack}\n*horse Version:* {selected_horse}\n*PI Version:* {selected_pi}\n*PSE Version:* {selected_pse}",
            attachments = BUTTON_ATTACHMENTS_NO_TEXT_ADDED
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
            selected_horse = submission["horse_spec"]
        if selected_pi == "specify":
            selected_pi = submission["pi_spec"]
        if selected_pse == "specify":
            selected_pse = submission["pse_spec"]
        # This sends out the add text/finish buttons
        if selection_value == "Clone and Upgrade":
            text = f"*Action:* {selection_value} Stack\n*Copy stack from:* {selected_from}\n*Copy stack to:* {selected_to}\n*horse Version:* {selected_horse}\n*PI Version:* {selected_pi}\n*PSE Version:* {selected_pse}",
            attachments = BUTTON_ATTACHMENTS_NO_TEXT_ADDED
        else:
            text = f"*Action:* {selection_value} Stack\n*Stack:* {selected_stack}\n*horse Version:* {selected_horse}\n*PI Version:* {selected_pi}\n*PSE Version:* {selected_pse}",
            attachments = BUTTON_ATTACHMENTS_NO_TEXT_ADDED
        # This opens the function that handles the clicking of add text/finish
        last_buttons = True

    SLACK_CLIENT.api_call(
        "chat.update",
        channel = "SAMPLE-CHANNEL",
        text = text,
        attachments = attachments
    )


def handle_interactive_message(form_json):
    if make_selection:
            selection_value = form_json["actions"][0]["selected_options"][0]["value"]

    # This opens the code versions box if necessary
    if next_button:
        if form_json["actions"][0]["value"] == "quit":
            done = True
            SLACK_CLIENT.api_call(
                "chat.update",
                channel = "SAMPLE-CHANNEL",
                attachments = [],
                text = "Ticket cancelled. Type *@doStack ticket* to start a new one."
            )
        else:
            # This turns on the function that handles the submission of this box
            print_next = True
            # This sends out the box
            SLACK_CLIENT.api_call(
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
            SLACK_CLIENT.api_call(
                "chat.update",
                channel = "SAMPLE-CHANNEL",
                attachments = [],
                text = "Ticket cancelled. Type *@doStack ticket* to start a new one."
            )
        else:
            # This ensures the code version submission handler isn't executed again
            print_next = False
            # This executes the handler for this box
            print_final = True
            # The following runs through every possible combination of specification selections
            # It then sends out the box with the necessary text fields that match the selections
            if selected_horse == "specify" and selected_pi == "specify" and selected_pse == "specify":
                SLACK_CLIENT.api_call(
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
                SLACK_CLIENT.api_call(
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
                SLACK_CLIENT.api_call(
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
                SLACK_CLIENT.api_call(
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
                SLACK_CLIENT.api_call(
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
                SLACK_CLIENT.api_call(
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
                SLACK_CLIENT.api_call(
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
            SLACK_CLIENT.api_call(
                "chat.update",
                channel = "SAMPLE-CHANNEL",
                attachments = [],
                text = "Ticket cancelled. Type *@doStack ticket* to start a new one."
            )
        else:
            edit_cau_info_submit = True
            SLACK_CLIENT.api_call(
                "dialog.open",
                trigger_id = form_json["trigger_id"],
                dialog = {
                    "title": f"{selection_value} Stack",
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
                    SLACK_CLIENT.api_call(
                        "dialog.open",
                        trigger_id = form_json["trigger_id"],
                        dialog = {
                            "title": f"{selection_value} Stack",
                            "Submit_label": "Submit",
                            "callback_id": "edit_first_no_add",
                            "elements": [
                                {
                                    "label": f"Stack to {selection_value}",
                                    "type": "text",
                                    "name": "edited_stack",
                                    "value": selected_stack
                                }
                            ]
                        }
                    )
                elif selection_value == "Clone":
                    SLACK_CLIENT.api_call(
                        "dialog.open",
                        trigger_id = form_json["trigger_id"],
                        dialog = {
                            "title": f"{selection_value} Stack",
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
                    SLACK_CLIENT.api_call(
                        "dialog.open",
                        trigger_id = form_json["trigger_id"],
                        dialog = {
                            "title": f"{selection_value} Stack",
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
                    SLACK_CLIENT.api_call(
                        "dialog.open",
                        trigger_id = form_json["trigger_id"],
                        dialog = {
                            "title": f"{selection_value} Stack",
                            "Submit_label": "Submit",
                            "callback_id": "edit_clone_and_upgrade_no_add",
                            "elements": [
                                {
                                    "label": f"Stack to {selection_value}",
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
                    SLACK_CLIENT.api_call(
                        "dialog.open",
                        trigger_id = form_json["trigger_id"],
                        dialog = {
                            "title": f"{selection_value} Stack",
                            "Submit_label": "Submit",
                            "callback_id": "edit_first_no_add",
                            "elements": [
                                {
                                    "label": f"Stack to {selection_value}",
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
                    SLACK_CLIENT.api_call(
                        "dialog.open",
                        trigger_id = form_json["trigger_id"],
                        dialog = {
                            "title": f"{selection_value} Stack",
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
                    SLACK_CLIENT.api_call(
                        "dialog.open",
                        trigger_id = form_json["trigger_id"],
                        dialog = {
                            "title": f"{selection_value} Stack",
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
                    SLACK_CLIENT.api_call(
                        "dialog.open",
                        trigger_id = form_json["trigger_id"],
                        dialog = {
                            "title": f"{selection_value} Stack",
                            "Submit_label": "Submit",
                            "callback_id": "edit_clone_and_upgrade_no_add",
                            "elements": [
                                {
                                    "label": f"Stack to {selection_value}",
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
                    SLACK_CLIENT.api_call(
                        "chat.update",
                        channel = "SAMPLE-CHANNEL",
                        attachments = [],
                        text = ":checkered_flag: Please copy and paste the following into <#C0UJWRKHU>:\n`/jirio create task {selection_value} {selected_stack}`"
                    )
                elif selection_value == "Clone":
                    SLACK_CLIENT.api_call(
                        "chat.update",
                        channel = "SAMPLE-CHANNEL",
                        attachments = [],
                        text = ":checkered_flag: Please copy and paste the following into <#C0UJWRKHU>:\n`/jirio create task {selection_value} Stack from {selected_from} to {selected_to}`"
                    )
                elif selection_value == "Clone and Upgrade":
                    SLACK_CLIENT.api_call(
                        "chat.update",
                        channel = "SAMPLE-CHANNEL",
                        attachments = [],
                        text = ":checkered_flag: Please copy and paste the following into <#C0UJWRKHU>:\n`/jirio create task {selection_value} Stack from {selected_from} to {selected_to}. Horse: {selected_horse} -- PI: {selected_pi} -- PSE: {selected_pse}`"
                    )
                else:
                    SLACK_CLIENT.api_call(
                        "chat.update",
                        channel = "SAMPLE-CHANNEL",
                        attachments = [],
                        text = ":checkered_flag: Please copy and paste the following into <#C0UJWRKHU>:\n`/jirio create task {selection_value} Stack {selected_stack} -- Horse: {selected_horse} -- PI: {selected_pi} -- PSE: {selected_pse}`"
                    )
            # This executes if the add text button was  clicked/extra info has been added
            else:
                # The following prints the jirio command based on your initial selection plus the extra info
                if selection_value == "Delete" or selection_value == "Archive" or selection_value == "Unarchive":
                    SLACK_CLIENT.api_call(
                        "chat.update",
                        channel = "SAMPLE-CHANNEL",
                        attachments = [],
                        text = ":checkered_flag: Please copy and paste the following into <#C0UJWRKHU>:\n`/jirio create task {selection_value} {selected_stack}. {selected_info}`"
                    )
                elif selection_value == "Clone":
                    SLACK_CLIENT.api_call(
                        "chat.update",
                        channel = "SAMPLE-CHANNEL",
                        attachments = [],
                        text = ":checkered_flag: Please copy and paste the following into <#C0UJWRKHU>:\n`/jirio create task {selection_value} Stack from {selected_from} to {selected_to}. {selected_info}`"
                    )
                elif selection_value == "Clone and Upgrade":
                    SLACK_CLIENT.api_call(
                        "chat.update",
                        channel = "SAMPLE-CHANNEL",
                        attachments = [],
                        text = ":checkered_flag: Please copy and paste the following into <#C0UJWRKHU>:\n`/jirio create task {selection_value} Stack from {selected_from} to {selected_to}. Horse: {selected_horse} -- PI: {selected_pi} -- PSE: {selected_pse}. {selected_info}`"
                    )
                else:
                    SLACK_CLIENT.api_call(
                        "chat.update",
                        channel = "SAMPLE-CHANNEL",
                        attachments = [],
                        text = ":checkered_flag: Please copy and paste the following into <#C0UJWRKHU>:\n`/jirio create task {selection_value} Stack {selected_stack} -- Horse: {selected_horse} -- PI: {selected_pi} -- PSE: {selected_pse}. {selected_info}`"
                    )
            # This opens the statement that starts the listener, essentially looping the bot after printing the ticket
            done = True
            
        # This handles the clicking of add button 
        elif form_json["actions"][0]["value"] == "add":
            # This enables the function that handles the submitted extra text
            print_add = True
            # This sends out the additional info text box
            SLACK_CLIENT.api_call(
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
            SLACK_CLIENT.api_call(
                "chat.update",
                channel = "SAMPLE-CHANNEL",
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
        SLACK_CLIENT.api_call(
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
        SLACK_CLIENT.api_call(
            "dialog.open",
            trigger_id = form_json["trigger_id"],
            dialog = {
                "title": "Stack to {selection_value}:",
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
        SLACK_CLIENT.api_call(
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