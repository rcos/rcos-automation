# RCOS Discord Automation
> Tools to automate the official RCOS Discord server.


# Features

## Member Registration
Previously it could be quite difficult determining the identity of an RCOS member from their Slack or Mattermost username. There was no explicit association between a member's chat account and their RPI identity.


### Joining the Server
This app associates RCOS members' Discord accounts with their RPI identities by requiring them to login with CAS and Discord before being added to the server.

### Nickname
Instead of allowing arbitrary nicknames, nicknames are generated for users when they login with CAS as `<First Name> <Last Name Initial> '<Graduation Year 2 Digits> (<RCS ID>)`, e.g. `Frank M '22 (matraf)` and members do not have permission to change their own nicknames once set. They can ask a coordinator to make changes if necessary. This means at a glance we never have to worry about finding out who somebody is when they need help, and RCOS members will know who they are collaborating with!

## Channel Generation
Small groups will get their own categories created to hold text and voice channels for their projects.

For example,

![example](https://snipboard.io/uL4yMk.jpg)

Each small group will have a general text channel and voice channel for standup and mentor help. Each project will have its own text channel and voice channel.

## Permissions
Custom roles are created for each **small group** and each **project**. The Discord role limit is 250 so for the time being we will not come close to hitting it. 

### Users
Users will be automatically assigned their small group and project roles. This means clicking a user will show their name, their RCS ID, their small group, and their project. This is a massive improvement!

### Categories/Channels
Small group categories will only be visible to their own members. Coordinators and faculty will be able to see all channels and categories at all times, though they can collapse categories to hide clutter.

This means the leadership will get a overall view of server activity while members only have access to what they need to prevent distraction.


## Scripts
To run a script, `$ python run_script.pt <script name>`
- `create_channels`
- `delete_channels`
- `generate_matterbridge_config`