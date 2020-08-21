import os
import sqlite3
from flask import Flask, g, session, request, render_template, redirect
from flask_cas import CAS, login_required, logout
from werkzeug.exceptions import HTTPException
from .discord import get_tokens, get_user_info, add_user_to_server, RCOS_SERVER_ID, DISCORD_REDIRECT_URL
from .db import query_db, get_db

app = Flask(__name__)
cas = CAS(app, '/cas')

app.secret_key = os.environ.get('SECRET_KEY')
app.config['CAS_SERVER'] = 'https://cas-auth.rpi.edu/cas'
app.config['CAS_AFTER_LOGIN'] = '/'


@app.route('/', methods=['GET', 'POST'])
@login_required
def join():
    if request.method == 'GET':
        row = query_db("SELECT discord_user_id FROM users WHERE rcs_id=?",
                       (cas.username.lower(),), True)

        if row == None:
            return render_template(
                'join.html',
                rcs_id=cas.username.lower()
            )
        else:
            return render_template('already_joined.html', rcs_id=cas.username.lower(), discord_server_id=RCOS_SERVER_ID)
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

        return redirect(DISCORD_REDIRECT_URL)


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
    try:
        c = get_db().cursor()
        c.execute('INSERT INTO users VALUES (?, ?)',
                  (cas.username.lower(), user['id']))
        get_db().commit()
        print(f'Added DB record for {cas.username}')
    except sqlite3.IntegrityError as err:
        print(f'Failed to add DB record for {cas.username}', err)
        return render_template('already_joined.html', rcs_id=cas.username.lower(), discord_server_id=RCOS_SERVER_ID)

    # Add user to server
    add_user_to_server(tokens['access_token'], user['id'], nickname)
    print(f'Added {cas.username} to the server as {nickname}')

    return render_template('done.html', nickname=nickname, discord_server_id=RCOS_SERVER_ID)


@app.route('/discord/reset', methods=['POST'])
@login_required
def discord_reset():
    # Delete DB record
    c = get_db().cursor()
    c.execute('DELETE FROM users WHERE rcs_id=?',
              (cas.username.lower(),))
    get_db().commit()

    return redirect('/')


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.errorhandler(Exception)
def handle_error(e):
    return render_template('error.html', error=e), 500
