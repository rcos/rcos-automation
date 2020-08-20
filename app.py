import os
import flask
from flask import Flask, request
from flask_cas import CAS, login_required, logout
import requests

app = Flask(__name__)
cas = CAS(app, '/cas')

app.secret_key = os.environ.get('SECRET_KEY')
app.config['CAS_SERVER'] = 'https://cas-auth.rpi.edu/cas'
app.config['CAS_AFTER_LOGIN'] = '/'

RCOS_SERVER_ID = os.environ.get('RCOS_SERVER_ID')
VERIFIED_ROLE_ID = os.environ.get('VERIFIED_ROLE_ID')
DISCORD_BOT_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
DISCORD_CLIENT_ID = os.environ.get('DISCORD_CLIENT_ID')
DISCORD_CLIENT_SECRET = os.environ.get('DISCORD_CLIENT_SECRET')
DISCORD_REDIRECT_URL = os.environ.get('DISCORD_REDIRECT_URL')


def get_tokens(code):
    '''Given an authorization code, request the access and refresh tokens for a Discord user. Returns the tokens. Throws an error if invalid request.'''

    response = requests.post(f'https://discord.com/api/oauth2/token',
                             data={
                                 'client_id': DISCORD_CLIENT_ID,
                                 'client_secret': DISCORD_CLIENT_SECRET,
                                 'grant_type': 'authorization_code',
                                 'code': code,
                                 'redirect_uri': 'http://localhost:5000/discord/callback',
                                 'scope': 'identity guilds.join'
                             },
                             headers={
                                 'Content-Type': 'application/x-www-form-urlencoded'
                             }
                             )
    response.raise_for_status()
    tokens = response.json()
    return tokens


def get_user_info(access_token):
    '''Given an access token, get a Discord user's info including id, username, discriminator, avatar url, etc. Throws an error if invalid request.'''
    response = requests.get('https://discordapp.com/api/users/@me',
                            headers={
                                'Authorization': f'Bearer {access_token}',
                                'Content-Type': 'application/json'
                            }
                            )
    response.raise_for_status()
    user = response.json()
    return user


def add_user_to_server(access_token, user_id):
    '''Given a Discord user's id, add them to the RCOS server with their nickname set as their RCS ID and with the 'Verified Student' role.'''
    response = requests.put(f'https://discordapp.com/api/guilds/{RCOS_SERVER_ID}/members/{user_id}',
                            json={
                                'access_token': access_token,
                                'nick': str(cas.username).lower(),
                                'roles': [VERIFIED_ROLE_ID],
                            },
                            headers={
                                'Authorization': f'Bot {DISCORD_BOT_TOKEN}'
                            }
                            )
    response.raise_for_status()
    return response


@app.route('/')
@login_required
def index():
    return flask.render_template(
        'index.html',
        username=cas.username,
        attributes=cas.attributes,
        discord_redirect_url=DISCORD_REDIRECT_URL
    )


@app.route('/discord/callback')
@login_required
def discord_callback():
    authorization_code = request.args.get('code')

    # Get access token
    tokens = get_tokens(authorization_code)

    # Get user id
    user = get_user_info(tokens['access_token'])

    # Add user to server
    add_user_to_server(tokens['access_token'], user['id'])

    return f'You\'ve been added to the RCOS server as {cas.username}'
