import datetime
import sys
import flask
import os
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from db.databaseNew import Database

load_dotenv()

OWNER_ID = os.getenv('owner_id', None)
GUI_PASSWORD = os.getenv('gui_password', None)
SECRET_KEY = os.getenv('secret_key', None)
if not SECRET_KEY:
    print("Error: No secret key provided. Check your environment variables.")
    sys.exit(1)

db = Database()

if os.name == 'nt':
    HOST = os.getenv('APP_HOST', "192.168.1.75")
    #PORT = os.getenv('APP_PORT')
else:
    HOST = os.environ.get('APP_HOST', "0.0.0.0")
    #PORT = os.getenv('APP_PORT')

PORT = os.getenv('APP_PORT', 5000)

app = flask.Flask(__name__, template_folder='./gui/templates', static_folder='./gui/static')
app.secret_key = SECRET_KEY

CORS(app, resources={r"/*": {"origins": "*"}})

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Return all errors in json format with error handler

@app.errorhandler(404)
def page_not_found(e):
    return flask.render_template('./errors/404.html'), 404

@app.errorhandler(401)
def access_denied(e):
    return flask.render_template('./errors/401.html'), 401

@app.route('/auth/login', methods=['GET', 'POST'])
def auth():
    if not OWNER_ID and not GUI_PASSWORD:
        return flask.render_template('./errors/configure.html')

    if flask.request.method == 'POST':
        password = flask.request.form['password']
        if password == GUI_PASSWORD:
            # Set session
            flask.session['logged_in'] = True
            flask.session['owner_id'] = OWNER_ID

            return flask.redirect('/dashboard')
        else:
            return flask.render_template('./auth/index.html', error="Invalid password")
    else:
        return flask.render_template('./auth/index.html')

@app.route('/auth/logout')
def logout():
    flask.session['logged_in'] = False
    flask.session['owner_id'] = None
    return flask.redirect('/auth/login')


@app.route('/dashboard')
def dashboard():
    # if not flask.session.get('logged_in'):
    #     return flask.redirect('/auth/login')

    return flask.render_template('./dashboard/index.html')


@app.route('/')
def index():
    return flask.redirect('/dashboard')

if __name__ == '__main__':
    try:
        port = int(PORT)  # Convert PORT to an integer
    except ValueError:
        print("Error: Invalid port number provided. Check your environment variables.")
        sys.exit(1)


    app.run(host=HOST, port=port, debug=True)