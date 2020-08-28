import os
from flask import Flask, g, session, request, render_template, redirect
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

    if request.method == 'GET':
        user = mongo.db.users.find_one({'rcs_id': cas.username.lower()})
        if user == None:
            return render_template(
                'join.html',
                rcs_id=cas.username.lower()
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

        session['user_info'] = {
            'first_name': first_name,
            'last_name': last_name,
            'graduation_year': graduation_year
        }
        session.modified = True

        user_data = {
            'rcs_id': cas.username.lower(),
            'name': {'first': first_name, 'last': last_name},
            'graduation_year': graduation_year
        }

        # Update or insert
        mongo.db.users.update_one({'rcs_id': cas.username.lower()}, {
                                  '$set': user_data}, upsert=True)

        return redirect(DISCORD_REDIRECT_URL)


@app.route('/connected')
@login_required
def connected():
    user = mongo.db.users.find_one({'rcs_id': cas.username.lower()})
    if user == None:
        return redirect('/')

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
    user = get_user_info(tokens['access_token'])

    # Generate Discord nickname to set as "<First Name> <Last Name Initial> '<Graduation Year 2 Digits> (<RCS ID>)"
    name = session['user_info']['first_name'] + ' ' + \
        session['user_info']['last_name'][0].upper()
    grad_year_digits = str(session['user_info']['graduation_year'])[2:]
    nickname = f'{name} \'{grad_year_digits} ({cas.username.lower()})'

    # Add to database
    mongo.db.users.update_one({'rcs_id': cas.username.lower()}, {'$set': {
        'discord': {
            'tokens': tokens,
            'user_id': user['id']
        }
    }})
    print(f'Added DB record for {cas.username}')

    # Add user to server
    add_user_to_server(tokens['access_token'], user['id'], nickname)
    print(f'Added {cas.username} to the server as {nickname}')

    return redirect('/connected')


@app.route('/discord/reset', methods=['POST'])
@login_required
def discord_reset():
    # Delete DB record
    # c = get_db().cursor()
    # c.execute('DELETE FROM users WHERE rcs_id=?',
    #           (cas.username.lower(),))
    # get_db().commit()

    mongo.db.users.delete_one({'rcs_id': cas.username.lower()})

    return redirect('/')


@app.errorhandler(Exception)
def handle_error(e):
    print(e)
    return render_template('error.html', error=e), 500
