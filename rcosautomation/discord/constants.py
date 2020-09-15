import os
from dotenv import load_dotenv
load_dotenv()


# Should be stored in .env
DISCORD_BOT_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')

# IDs
RCOS_SERVER_ID = os.environ.get('RCOS_SERVER_ID')
SMALL_GROUPS_CATEGORY_ID = os.environ.get('SMALL_GROUPS_CATEGORY_ID')
DISCORD_PM_ROLE_ID = os.environ.get('DISCORD_PM_ROLE_ID')
PROTECTED_CHANNEL_IDS = os.environ.get(
    'DISCORD_PROTECTED_CHANNEL_IDS').split(',')

# CHANNEL TYPES
# https://discord.com/developers/docs/resources/channel#channel-object-channel-types
TEXT_CHANNEL = 0
VOICE_CHANNEL = 2
CATEGORY = 4

CHANNEL_TYPES = {
    0: 'Text',
    2: 'Voice',
    4: 'Category'
}

# AUTHORIZATION
HEADERS = {
    'Authorization': f'Bot {DISCORD_BOT_TOKEN}',
}
MATTERMOST_USERNAME = os.environ['MATTERMOST_USERNAME']
MATTERMOST_PASSWORD = os.environ['MATTERMOST_PASSWORD']

# PERMISSIONS
VIEW_CHANNELS = 0x00000400
MANAGE_MESSAGES = 0x00002000
