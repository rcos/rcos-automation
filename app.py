from dotenv import load_dotenv
load_dotenv()

import os
from flask import Flask, session, request, render_template, redirect
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


def add_user_to_server(access_token: str, user_id: str, nickname: str):
    '''Given a Discord user's id, add them to the RCOS server with their nickname set as their RCS ID and with the 'Verified Student' role.'''
    response = requests.put(f'https://discordapp.com/api/guilds/{RCOS_SERVER_ID}/members/{user_id}',
                            json={
                                'access_token': access_token,
                                'nick': nickname,
                                'roles': [VERIFIED_ROLE_ID],
                            },
                            headers={
                                'Authorization': f'Bot {DISCORD_BOT_TOKEN}'
                            }
                            )
    response.raise_for_status()
    print(f'Added user {nickname} to server')
    return response


@app.route('/', methods=['GET', 'POST'])
@login_required
def join():
    if request.method == 'GET':
        return render_template(
            'join.html',
            rcs_id=cas.username.lower()
        )
    elif request.method == 'POST':
        session['user_info'] = {
            'first_name': request.form['first_name'].strip(),
            'last_name': request.form['last_name'].strip(),
            'graduation_year': int(request.form['graduation_year'])
        }
        session.modified = True

        return redirect(DISCORD_REDIRECT_URL)


@app.route('/discord/callback')
@login_required
def discord_callback():
    authorization_code = request.args.get('code')

    # Get access token
    tokens = get_tokens(authorization_code)
    session['tokens'] = tokens

    # Get user id
    user = get_user_info(tokens['access_token'])

    # Generate Discord nickname to set as "<First Name> <Last Name Initial> '<Graduation Year 2 Digits> (<RCS ID>)"
    name = session['user_info']['first_name'] + ' ' + session['user_info']['last_name'][0].upper()
    grad_year_digits = str(session['user_info']['graduation_year'])[2:]
    nickname = f'{name} \'{grad_year_digits} ({cas.username.lower()})'
    
    # Add user to server
    add_user_to_server(tokens['access_token'], user['id'], nickname)

    return render_template('done.html', nickname=nickname, discord_server_id=RCOS_SERVER_ID)
