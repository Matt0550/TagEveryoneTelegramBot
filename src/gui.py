import datetime
import sys
import flask
import os
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from db.databaseNew import Database
import hmac
import hashlib
from urllib.parse import unquote

load_dotenv()

OWNER_ID = os.getenv('owner_id', None)
GUI_PASSWORD = os.getenv('gui_password', None)
SECRET_KEY = os.getenv('secret_key', None)
TOKEN = os.getenv('token', None)

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



## METHODS

def validate(hash_str, init_data, c_str="WebAppData"):
    """
    Validates the data received from the Telegram web app, using the
    method documented here: 
    https://core.telegram.org/bots/webapps#validating-data-received-via-the-web-app

    hash_str - the has string passed by the webapp
    init_data - the query string passed by the webapp
    c_str - constant string (default = "WebAppData")
    """

    init_data = sorted([ chunk.split("=") 
          for chunk in unquote(init_data).split("&") 
            if chunk[:len("hash=")]!="hash="],
        key=lambda x: x[0])
    init_data = "\n".join([f"{rec[0]}={rec[1]}" for rec in init_data])

    secret_key = hmac.new(c_str.encode(), TOKEN.encode(),
        hashlib.sha256 ).digest()
    data_check = hmac.new( secret_key, init_data.encode(),
        hashlib.sha256)

    return data_check.hexdigest() == hash_str

def queryToDict(query):
    """
    Converts a query string to a dictionary
    """
    query = query.split('&')
    query = [q.split('=') for q in query]
    query = {q[0]: q[1] for q in query}
    return query

def getUserFromQuery(query):
    """
    Gets the user from the query string
    """
    query = queryToDict(query)
    user = query['user']
    user = unquote(user)
    # Replace true and false with True and False
    user = user.replace('true', 'True')
    user = user.replace('false', 'False')
    user = eval(user)
    return user
    
## ROUTES

# Return all errors in json format with error handler

@app.errorhandler(404)
def page_not_found(e):
    return flask.jsonify({'status': 404, 'message': 'Not Found'}), 404

@app.errorhandler(401)
def access_denied(e):
    return flask.jsonify({'status': 401, 'message': 'Unauthorized'}), 401

@app.route('/getInGroups', methods=['POST'])
def getInGroups():
    # Validate telegram webapp data
    # Get body
    body = flask.request.get_json()
    # Validate hash
    hash_str = body['hash']
    init_data = body['init_data']

    print("Hash: ", hash_str)
    print("Init data: ", init_data)

    
    if not validate(hash_str, init_data):
        flask.abort(401)

    userId = getUserFromQuery(init_data)
    groupsIn = db.getGroupsOfUser(userId["id"])
    # To json
    groupsIn = [{'group_id': group[1], 'name': group[2], 'members': group[6]} for group in groupsIn]
    # JSON 200
    return flask.jsonify({'status': 200, 'groups': groupsIn})

@app.route('/')
def dashboard():

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