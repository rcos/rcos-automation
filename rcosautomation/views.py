import os
from flask import Flask, session, request, render_template, redirect
from flask_cas import CAS, login_required, logout
from .discord import get_tokens, get_user_info, add_user_to_server, RCOS_SERVER_ID, DISCORD_REDIRECT_URL

app = Flask(__name__)
cas = CAS(app, '/cas')

app.secret_key = os.environ.get('SECRET_KEY')
app.config['CAS_SERVER'] = 'https://cas-auth.rpi.edu/cas'
app.config['CAS_AFTER_LOGIN'] = '/'


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
    name = session['user_info']['first_name'] + ' ' + \
        session['user_info']['last_name'][0].upper()
    grad_year_digits = str(session['user_info']['graduation_year'])[2:]
    nickname = f'{name} \'{grad_year_digits} ({cas.username.lower()})'

    # Add user to server
    add_user_to_server(tokens['access_token'], user['id'], nickname)

    return render_template('done.html', nickname=nickname, discord_server_id=RCOS_SERVER_ID)
