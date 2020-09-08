'''
This script is used to generate a valid matterbridge.toml file to let Matterbridge know what
channels to bridge between Discord and Mattermost. It requires a Discord bot and a dedicated
Mattermost user account. It outputs a valid toml file that must be pointed to when running matterbridge.

Environment Variables (if not set the program will prompt the user for them):
MATTERBRIDGE_DISCORD_TOKEN: 
MATTERBRIDGE_DISCORD_SERVER_ID
MATTERBRIDGE_DISCORD_PREFIX
MATTERBRIDGE_MATTERMOST_USERNAME
MATTERBRIDGE_MATTERMOST_PASSWORD

matterbridge: https://github.com/42wim/matterbridge/wiki
tomlkit: https://github.com/sdispater/tomlkit
'''
from tomlkit import parse, dumps, document, table, comment, aot
import os
from dotenv import load_dotenv
load_dotenv()

# Constants
DEFAULT_REMOTE_NICKNAME_FORMAT = '**{NICK}**: '


def get_from_env_or_input(key: str, prompt: str, default=None):
    '''Get a value from either an environment variable or user input. Can be given a default value if user enters nothing.'''

    # If there's a default value, show it at the end of the prompt
    if not default == None:
        prompt += f'[default: "{default}"]'

    # Try to get value from env
    value = os.environ.get(key)
    if value == None:
        if default == None:
            # If no default and not in env, keep prompting until user enters a value
            value = input(prompt)
            while len(value) == 0:
                value = input(prompt)
        else:
            # If default is supplied, use user input or default
            value = input(prompt)
            if len(value) == 0:
                value = default

    return value


def run():
    # The toml document
    doc = document()

    # General settings
    doc['general'] = table()
    doc['general']['IgnoreFailureOnStart'] = False

    # DISCORD
    print('Let\'s setup Discord...')
    doc['discord'] = table()
    doc['discord'].comment('Discord server connection settings')
    doc['discord']['rcos'] = table()

    doc['discord']['rcos']['Token'] = get_from_env_or_input(
        'MATTERBRIDGE_DISCORD_TOKEN', 'Bot Token: ')
    doc['discord']['rcos']['Token'].comment(
        'SECRET bot token found on https://discord.com/developers')

    doc['discord']['rcos']['Server'] = get_from_env_or_input(
        'MATTERBRIDGE_DISCORD_SERVER_ID', 'Server: ')
    doc['discord']['rcos']['Server'].comment(
        'The ID of the Discord server. Can be found in URL when on Discord or if Developer Mode is turned on and right-clicking the server icon.')

    doc['discord']['rcos']['RemoteNickFormat'] = get_from_env_or_input(
        'MATTERBRIDGE_DISCORD_PREFIX', 'Message prefix: ', default=DEFAULT_REMOTE_NICKNAME_FORMAT)
    doc['discord']['rcos']['RemoteNickFormat'].comment(
        'The prefix to apply to messages.')

    # MATTERMOST
    print('\n\nNow Mattermost...')
    doc['mattermost'] = table()
    doc['mattermost'].comment('Mattermost server connection settings')
    doc['mattermost']['rcos'] = table()

    doc['mattermost']['rcos']['Server'] = 'chat.rcos.io:443'
    doc['mattermost']['rcos']['Server'].comment(
        'URL of the Mattermost server with no http:// or https:// prepended')

    doc['mattermost']['rcos']['Team'] = 'rcos'
    doc['mattermost']['rcos']['Team'].comment(
        'The "team", found as the first part of URL when on Mattermost server')

    doc['mattermost']['rcos']['Login'] = get_from_env_or_input(
        'MATTERBRIDGE_MATTERMOST_USERNAME', 'Username: ')
    doc['mattermost']['rcos']['Login'].comment(
        'Mattermost needs a user account to send/receive messages. This is the account username.')

    doc['mattermost']['rcos']['Password'] = get_from_env_or_input(
        'MATTERBRIDGE_MATTERMOST_PASSWORD', 'Password: ')
    doc['mattermost']['rcos']['Password'].comment(
        'The password of the Mattermost account to use.')

    doc['mattermost']['rcos']['RemoteNickFormat'] = get_from_env_or_input(
        'MATTERBRIDGE_MATTERMOST_PREFIX', 'Message prefix: ', default=DEFAULT_REMOTE_NICKNAME_FORMAT)
    doc['mattermost']['rcos']['RemoteNickFormat'].comment(
        'The prefix to apply to messages.')

    # The channels to pair
    # (Discord channel, Mattermost channel)
    channel_pairs = []
    print("Enter the channels you want to pair on each line and enter an empty line to finish.\nDiscord,Mattermost")

    line = input()
    while len(line) > 0:
        channel_pairs.append(line.split(","))
        line = input()

    gateways = aot()

    # Create the gateways in the document
    for index, pair in enumerate(channel_pairs):
        gateway = table()
        gateway['name'] = f'gateway-{index}'
        gateway['enable'] = True

        # inout means that messages are sent/received both ways
        gateway['inout'] = aot()
        gateway_discord = table()
        gateway_discord['account'] = 'discord.rcos'
        gateway_discord['channel'] = pair[0]
        gateway['inout'].append(gateway_discord)

        gateway_mattermost = table()
        gateway_mattermost['account'] = 'mattermost.rcos'
        gateway_mattermost['channel'] = pair[1]
        gateway['inout'].append(gateway_mattermost)

        gateways.append(gateway)

    doc.add('gateway', gateways)

    # Write the output to a file
    with open('matterbridge.toml', 'w') as outfile:
        outfile.write(dumps(doc))
        print(
            'Wrote output to matterbridge.toml. Now place it where Matterbridge wants it!')
