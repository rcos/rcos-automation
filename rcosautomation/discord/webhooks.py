import requests
from .constants import DISCORD_ERROR_WEBHOOK_URL


def send_webhook_message(message: str):
    '''Send webhook message to the specified webhook URL.'''
    response = requests.post(DISCORD_ERROR_WEBHOOK_URL,
                             json={
                                 'username': 'Discord+CAS Logs',
                                 'content': message
                             })
    response.raise_for_status()
    return response
