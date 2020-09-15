import requests
import re
from typing import List, Dict, Optional
from .constants import RCOS_SERVER_ID, HEADERS, TEXT_CHANNEL, VOICE_CHANNEL, CHANNEL_TYPES


def generate_text_channel_name(name: str) -> str:
    '''Given a name, convert it into what its Discord text channel title would be.'''
    no_white_space = re.sub(r'\W+', ' ', name)
    stripped = no_white_space.strip()
    no_nonalphanum = re.sub(r'\s+', '-', stripped)
    lowercased = no_nonalphanum.lower()
    return lowercased


def get_all_channels() -> List:
    '''Get all channels on the server.'''
    response = requests.get(
        f'https://discordapp.com/api/guilds/{RCOS_SERVER_ID}/channels', headers=HEADERS)
    response.raise_for_status()
    return response.json()


def add_channel(name: str, channel_type: int = TEXT_CHANNEL, topic: str = None, parent_id=None, perms=None) -> Dict:
    '''Add a channel or category to the server.'''
    response = requests.post(f'https://discordapp.com/api/guilds/{RCOS_SERVER_ID}/channels',
                             json={
                                 'name': name,
                                 'type': channel_type,
                                 'topic': topic,
                                 'parent_id': parent_id,
                                 'permission_overwrites': perms
                             },
                             headers=HEADERS
                             )
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


def add_channel_if_not_exists(name: str, channel_type: int = TEXT_CHANNEL, topic: str = None, parent_id=None, perms=None) -> Dict:
    '''Add a channel if it does not already exist.'''
    # See if channel exists
    channel = find_channel(
        name, channel_type=channel_type, parent_id=parent_id)

    if channel == None:
        channel = add_channel(name, channel_type=channel_type,
                              topic=topic, parent_id=parent_id, perms=perms)
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


def get_all_roles() -> List:
    '''Get all roles on the server.'''
    response = requests.get(
        f'https://discordapp.com/api/guilds/{RCOS_SERVER_ID}/roles', headers=HEADERS)
    response.raise_for_status()
    return response.json()


def add_role(name: str, hoist=False) -> Dict:
    '''Add a new role to the server.'''
    response = requests.post(
        f'https://discordapp.com/api/guilds/{RCOS_SERVER_ID}/roles', json={'name': name, 'hoist': hoist}, headers=HEADERS)
    response.raise_for_status()
    return response.json()


def find_role(name) -> Optional[Dict]:
    '''Find a role and return it if it exists. Otherwise returns None.'''
    for role in all_roles:
        if role['name'] == name:
            return role
    return None


def add_role_if_not_exists(name: str, hoist=False) -> Dict:
    '''Add a new role to the server if it doesn't exist. Returns the created or existing role.'''
    role = find_role(name)
    if role == None:
        role = add_role(name, hoist=hoist)
        all_roles.append(role)

    return role


all_channels = get_all_channels()
all_roles = get_all_roles()