import os
import traceback
from flask import Flask, g, session, request, render_template, redirect, url_for
from flask_cas import CAS, login_required, logout
from werkzeug.exceptions import HTTPException
from .discord import get_tokens, get_user_info, add_user_to_server, RCOS_SERVER_ID, DISCORD_REDIRECT_URL
from flask_pymongo import PyMongo
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
cas = CAS(app, '/cas')
app.config['MONGO_URI'] = os.environ.get('MONGO_URI')
mongo = PyMongo(app)

app.secret_key = os.environ.get('SECRET_KEY')
app.config['CAS_SERVER'] = 'https://cas-auth.rpi.edu/cas'
app.config['CAS_AFTER_LOGIN'] = '/'


@app.route('/', methods=['GET', 'POST'])
@login_required
def join():
    alert = request.args.get('alert')
    if request.method == 'GET':
        user = mongo.db.users.find_one({'rcs_id': cas.username.lower()})
        if user == None:
            mongo.db.users.insert_one({ 'rcs_id': cas.username.lower(), 'name': {}, 'graduation_year': 2020 })
            user = mongo.db.users.find_one({'rcs_id': cas.username.lower()})
            print('Created ', user)
        if 'discord' not in user:
            return render_template(
                'join.html',
                user=user,
                rcs_id=cas.username.lower(),
                alert=alert
            )
        else:
            return redirect('/connected')
    elif request.method == 'POST':
        # Get fields from form data and sanitize
        try:
            # Limit to 20 characters so overall Discord nickname doesn't exceed limit of 32 characters
            first_name = request.form['first_name'].strip()[:20]
            last_name = request.form['last_name'].strip()
            graduation_year = int(request.form['graduation_year'].strip())
        except:
            # Not all fields given?
            return render_template(
                'join.html',
                rcs_id=cas.username.lower(),
                error_message='Make sure all fields are filled!'
            )

        print(f'{cas.username} is starting to connect their Discord account with the identity {first_name} {last_name} \'{graduation_year}')

        user_data = {
            'rcs_id': cas.username.lower(),
            'name': {'first': first_name, 'last': last_name},
            'graduation_year': graduation_year
        }

        # Update or insert
        mongo.db.users.update_one({'rcs_id': cas.username.lower()}, {
                                  '$set': user_data})

        return redirect(DISCORD_REDIRECT_URL)


@app.route('/connected')
@login_required
def connected():
    user = mongo.db.users.find_one({'rcs_id': cas.username.lower()})
    if user == None or 'discord' not in user:
        return redirect(url_for('join', alert='You are not connected yet!'))

    return render_template('connected.html', user=user, discord_server_id=RCOS_SERVER_ID)


@app.route('/discord/callback')
@login_required
def discord_callback():
    authorization_code = request.args.get('code')
    error = request.args.get('error')

    if error:
        error_description = request.args.get('error_description')
        print(
            f'An error occurred when authenticating with Discord for {cas.username}: ({error}) {error_description}')
        error_message = 'You refused to connect your Discord account!' if error == 'access_denied' else 'Something went wrong when connecting your Discord account. Please try again later.'
        raise Exception(error_message)

    # Get access token
    tokens = get_tokens(authorization_code)
    session['tokens'] = tokens

    # Get user id
    discord_user = get_user_info(tokens['access_token'])
    
    user = mongo.db.users.find_one({'rcs_id': cas.username.lower()})
    # Generate Discord nickname to set as "<First Name> <Last Name Initial> '<Graduation Year 2 Digits> (<RCS ID>)"
    
    
    name = user['name']['first'] + ' ' + user['name']['last'][0].upper()
    grad_year_digits = str(user['graduation_year'])[2:]
    nickname = f'{name} \'{grad_year_digits} ({cas.username.lower()})'

    # Add to database
    mongo.db.users.find_one_and_update({'rcs_id': cas.username.lower()}, {'$set': {
        'discord': {
            'tokens': tokens,
            'user_id': discord_user['id']
        }
    }})
    print(f'Added DB record for {cas.username}')

    # Add user to server
    add_user_to_server(tokens['access_token'], discord_user['id'], nickname)
    print(f'Added {cas.username.lower()} to the server as {nickname}')

    return redirect('/connected')


@app.route('/discord/reset', methods=['POST'])
@login_required
def discord_reset():
    # Delete Discord data from user
    mongo.db.users.update_one({'rcs_id': cas.username.lower()}, {
        '$unset': {'discord': True}
    })

    return redirect('/')


@app.errorhandler(Exception)
def handle_error(e):
    print(e)
    print(traceback.format_exc())

    # Hide error in production
    error = e
    if app.config['ENV'] == 'development':
        error = 'Something went wrong... Please try again later.'

    return render_template('error.html', error=error), 500
