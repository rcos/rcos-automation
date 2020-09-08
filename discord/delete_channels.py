from .constants import *
import requests


def get_channel(channel_id: str):
    response = requests.get(
        f'https://discordapp.com/api/channels/{channel_id}', headers=HEADERS)
    response.raise_for_status()
    return response.json()


def get_category_children(category_id: str):
    # Get all children
    response = requests.get(
        f'https://discordapp.com/api/guilds/{RCOS_SERVER_ID}/channels', headers=HEADERS)
    response.raise_for_status()
    channels = response.json()
    # Filter to find children
    children = filter(
        lambda channel: channel['parent_id'] == category_id, channels)
    return children


def delete_channel(channel_id: str):
    # Check if this channel or its parent is protected
    if channel_id in PROTECTED_CHANNEL_IDS:
        raise Exception('Cannot delete protected channel')

    channel = get_channel(channel_id)

    if channel['parent_id'] in PROTECTED_CHANNEL_IDS:
        raise Exception('Cannot delete channel in protected category')

    response = requests.delete(
        f'https://discordapp.com/api/channels/{channel_id}', headers=HEADERS)
    response.raise_for_status()
    return response.json()


def run():
    while True:
        channel_id = input(
            'What is the ID of the channel you want to delete?\n>')

        try:
            channel = get_channel(channel_id)
        except:
            print(f'Failed to find channel with ID {channel_id}')
            continue

        delete_count = 0

        # If channel is a category, ask to delete all children channels since it is not done by default
        if channel['type'] == CATEGORY:

            delete_children = input(
                f'Channel `{channel["name"]}` is a category. Delete all children(Y) or just the category(N)\n>')

            if delete_children == 'Y':
                print('Deleting children')
                try:
                    children = get_category_children(channel_id)
                    for child in children:
                        try:
                            delete_channel(child['id'])
                            delete_count += 1
                        except:
                            print(
                                f'Failed to delete child channel `{child["name"]}`')
                except:
                    print('Failed to find children channels')
            else:
                print('Not deleting children channels')

        # Delete channel
        try:
            delete_channel(channel_id)
            delete_count += 1
            print(
                f'Deleted `{channel["name"]}` ({delete_count} channels total)')
        except:
            print(
                f'Failed to delete `{channel["name"]}`. Deleted {delete_count} channels total')
