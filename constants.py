# A Dictionary of initial message options
ACTION_ATTACHMENTS = [
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

ACTION_OPTIONS = {
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

# The attachment for all buttons minus the preview button
BUTTON_ATTACHMENTS_TEXT_ADDED = [
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

# The attachment for edit, finish, and cancel buttons
BUTTON_ATTACHMENTS_NO_TEXT_ADDED = [
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

# The attachment for the next button
NEXT_BUTTON_ATTACHMENTS = [
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