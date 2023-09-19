# ticket-handling-slack-botz
This Slack bot was the first iteration of an automated ticket handling product created for a previous employer.

Written in Python in the summer of 2018, the bot allowed the user to select from a handful of different options, spanning from stack creation, to data migration, to account creation. Based on the user's selection, the bot would dynamically populate further questions and fields for the user to fill out. The true automation behind the bot was severely lacking, as the end result of the user's actions was a Jira ticket being filed with our DevOps team.

This bot however was the first small step on a long road of fully automating all manual ticket handling by our DevOps team. The final state of this project was a full fledge Angular web app with a complex API layer and a Python backend running on Jenkins. That final state is still in use by my previous employer, and currently supports over 75 complex actions, automating an average of over 2 daily tickets per employee.

The code is lacking in organization, and would dramatically benefit from abstractions which could make it easily extendable. However, this code continues to serve as a reminder of how far my code's quality has come since I began programming mere months before writing this.

Values and variables have been changed to protect company data and privacy.
