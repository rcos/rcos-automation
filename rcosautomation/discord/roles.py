import requests
from typing import List, Dict, Optional
from .constants import RCOS_SERVER_ID, HEADERS


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


all_roles = get_all_roles()
