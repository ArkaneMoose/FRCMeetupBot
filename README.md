# FRC Meetup Bot

A bot for Discord that automatically calculates potential meetups for FRC teams.

## Things it does

* Uses regular expressions to try to find the team number in someone's nick.
* Validates that team number using The Blue Alliance's API.
* Fetches every team's events using The Blue Alliance's API.
* Filters only for a certain week.
* Calculates all the teams going to each event.
* Spits that data back into the Discord chat.

## Things I want it to do

* Allow people to specify their team number or that they are not in an FRC team.
* Allow people to specify that they are attending or not attending a specific
  event, even if their team is or is not attending.
* Edit its own messages if someone makes a correction to their team number or
  their events.
* Automatically tag people with event-specific tags.
* Automatically try to detect if someone is not in an FRC team (e.g. if their
  username contains "FTC" and not "FRC").
* Have the bot always run and post the week's events at some time that week.
