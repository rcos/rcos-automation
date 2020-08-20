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

@app.route('/')
@login_required
def index():
    return flask.render_template(
        'index.html',
        username = cas.username,
        attributes = cas.attributes,
        discord_redirect_url=DISCORD_REDIRECT_URL
    )

@app.route('/discord/callback')
@login_required
def discord_callback():
    authorization_code = request.args.get('code')

    # Get access token
    response = requests.post(f'https://discord.com/api/oauth2/token',
        data={
            'client_id': DISCORD_CLIENT_ID,
            'client_secret': DISCORD_CLIENT_SECRET,
            'grant_type': 'authorization_code',
            'code': authorization_code,
            'redirect_uri': 'http://localhost:5000/discord/callback',
            'scope': 'identity guilds.join'
        },
        headers={
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    )
    response.raise_for_status()
    tokens = response.json()

    # Get user id
    response = requests.get('https://discordapp.com/api/users/@me',
        headers={
            'Authorization': 'Bearer ' + tokens['access_token'],
            'Content-Type': 'application/json'
        }
    )
    response.raise_for_status()
    data = response.json()

    response = requests.put(f'https://discordapp.com/api/guilds/{RCOS_SERVER_ID}/members/{data["id"]}',
        json={
            'access_token': tokens['access_token'],
            'nick': str(cas.username).lower(),
            'roles': [VERIFIED_ROLE_ID],
        },
        headers={
            'Authorization': f'Bot {DISCORD_BOT_TOKEN}'
        }
    )
    response.raise_for_status()

    return f'You\'ve been added to the RCOS server as {cas.username}'