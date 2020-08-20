from enum import Enum
import re
import os
import requests
from csv import DictReader
from typing import List, Dict, Optional
from dotenv import load_dotenv
load_dotenv()


# Should be stored in .env
RCOS_SERVER_ID = os.environ.get('RCOS_SERVER_ID')
DISCORD_BOT_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
SMALL_GROUPS_CATEGORY_ID = os.environ.get('SMALL_GROUPS_CATEGORY_ID')

# https://discord.com/developers/docs/resources/channel#channel-object-channel-types
TEXT_CHANNEL = 0
VOICE_CHANNEL = 2
CATEGORY = 4

HEADERS = {
    'Authorization': f'Bot {DISCORD_BOT_TOKEN}',
}


def generate_text_channel_name(name: str) -> str:
    '''Given a name, convert it into what its Discord text channel title would be.'''
    no_white_space = re.sub(r'\W+', ' ', name)
    stripped = no_white_space.strip()
    no_nonalphanum = re.sub(r'\s+', '-', stripped)
    lowercased = no_nonalphanum.lower()
    return lowercased


def get_all_channels() -> List:
    '''Get all channels on the RCOS server.'''
    response = requests.get(
        f'https://discordapp.com/api/guilds/{RCOS_SERVER_ID}/channels', headers=HEADERS)
    response.raise_for_status()
    return response.json()


def find_channel(name: str, channel_type: int, parent_id=None) -> Optional[Dict]:
    '''Find and return a channel with the given criteria or return None'''
    if channel_type == TEXT_CHANNEL:
        name = generate_text_channel_name(name)
    for channel in all_channels:
        if channel['type'] == channel_type and channel['name'] == name and channel['parent_id'] == parent_id:
            return channel
    return None


def add_channel(name: str, channel_type: int = TEXT_CHANNEL, topic: str = None, parent_id=None) -> Dict:
    '''Add a channel or category to the server.'''
    response = requests.post(f'https://discordapp.com/api/guilds/{RCOS_SERVER_ID}/channels',
                             json={
                                 'name': name,
                                 'type': channel_type,
                                 'topic': topic,
                                 'parent_id': parent_id
                             },
                             headers=HEADERS
                             )
    response.raise_for_status()
    return response.json()


def add_channel_if_not_exists(name: str, channel_type: int = TEXT_CHANNEL, topic: str = None, parent_id=None) -> Dict:
    # See if channel exists
    channel = find_channel(
        name, channel_type=channel_type, parent_id=parent_id)

    CHANNEL_TYPES = {
        0: 'Text',
        2: 'Voice',
        4: 'Category'
    }

    if channel == None:
        channel = add_channel(name, channel_type=channel_type,
                              topic=topic, parent_id=parent_id)
        all_channels.append(channel)
        print(
            f'{CHANNEL_TYPES[channel["type"]]} "{channel["name"]}" was added')
    else:
        print(
            f'{CHANNEL_TYPES[channel["type"]]} "{channel["name"]}" already exists')
    return channel


def delete_channel(channel_id) -> Dict:
    response = requests.delete(f'https://discordapp.com/api/channels/{channel_id}',
                               headers=HEADERS
                               )
    response.raise_for_status()
    return response.json()


all_channels = get_all_channels()
# all_roles = get_all_roles()

if __name__ == '__main__':
    students = dict()
    small_groups = dict()

    with open('students.csv', 'r') as file:
        csv_reader = DictReader(file)
        for row in csv_reader:
            students[row['rcs_id']] = row

            if row['small_group'] not in small_groups:
                small_groups[row['small_group']] = set()

            small_groups[row['small_group']].add(row['project'])

    for small_group in small_groups:
        title = f'Small Group {small_group}'

        # Create category for small group to hold general and project channels
        small_group_category = add_channel_if_not_exists(
            title, CATEGORY)

        # Create role
        # add_role_if_not_exists(title)

        # Create this small group's general channels
        small_group_text_channel = add_channel_if_not_exists(
            title, parent_id=small_group_category['id'])
        small_group_voice_channel = add_channel_if_not_exists(
            title, channel_type=VOICE_CHANNEL, parent_id=small_group_category['id'])

        # Create this small group's project channels
        for project in small_groups[small_group]:
            project_text_channel = add_channel_if_not_exists(
                project, channel_type=TEXT_CHANNEL, topic=f'🗨️ Discussion channel for {project}', parent_id=small_group_category['id'])
            project_voice_channel = add_channel_if_not_exists(
                project, channel_type=VOICE_CHANNEL, parent_id=small_group_category['id'])
