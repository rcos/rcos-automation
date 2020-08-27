import requests
import os
from dotenv import load_dotenv
load_dotenv()


TEXT_CHANNEL = 0
VOICE_CHANNEL = 2
CATEGORY = 4
RCOS_SERVER_ID = os.environ.get('RCOS_SERVER_ID')
DISCORD_BOT_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
HEADERS = {
    'Authorization': f'Bot {DISCORD_BOT_TOKEN}',
}


def get_channel(channel_id: str):
    response = requests.get(
        f'https://discordapp.com/api/channels/{channel_id}', headers=HEADERS)
    response.raise_for_status()
    return response.json()

def get_category_children(category_id: str):
    # Get all children
    response = requests.get(f'https://discordapp.com/api/guilds/{RCOS_SERVER_ID}/channels', headers=HEADERS)
    response.raise_for_status()
    channels = response.json()
    # Filter to find children
    children = filter(lambda channel: channel['parent_id'] == category_id, channels)
    return children

def delete_channel(channel_id: str):
    response = requests.delete(
        f'https://discordapp.com/api/channels/{channel_id}', headers=HEADERS)
    response.raise_for_status()
    return response.json()


while True:
    channel_id = input('What is the ID of the channel you want to delete?\n>')
    channel = get_channel(channel_id)

    delete_count = 0

    # If channel is a category, ask to delete all children channels since it is not done by default
    if channel['type'] == CATEGORY:
        
        delete_children = input(
            f'Channel `{channel["name"]}` is a category. Delete all children(Y) or just the category(N)\n>')
        
        if delete_children == 'Y':
            print('Deleting children')
            children = get_category_children(channel_id)
            for child in children:
                delete_channel(child['id'])
                delete_count += 1
        else:
            print('Not deleting children channels')

    # Delete channel
    delete_channel(channel_id)
    delete_count += 1

    print(f'Deleted `{channel["name"]}` ({delete_count} channels total)')