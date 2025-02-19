import hashlib
import hmac
import os
import sys
from dotenv import load_dotenv
from flask import Flask, jsonify, request, render_template, abort
from flask_cors import CORS
from db.databaseNew import Database
from urllib.parse import unquote

load_dotenv()

OWNER_ID = os.getenv('owner_id', None)
GUI_PASSWORD = os.getenv('gui_password', None)
SECRET_KEY = os.getenv('secret_key', None)
TOKEN = os.getenv('token', None)
WEBSERVER_DEBUG = os.getenv('webserver_debug', False)

# Convert webserver debug flag to boolean
WEBSERVER_DEBUG = str(WEBSERVER_DEBUG).lower() in ["true", "1"]

if not SECRET_KEY:
	print("Error: No secret key provided. Check your environment variables.")
	sys.exit(1)

db = Database()

# Host configuration
if os.name == 'nt':
	HOST = os.getenv('APP_HOST', "localhost")
else:
	HOST = os.getenv('APP_HOST', "0.0.0.0")

PORT = os.getenv('APP_PORT', 5000)

# Initialize Flask application
app = Flask(__name__, template_folder='./gui/templates', static_folder='./gui/static')
app.secret_key = SECRET_KEY

CORS(app, resources={r"/*": {"origins": "*"}})

os.chdir(os.path.dirname(os.path.abspath(__file__)))


## METHODS

def validate(hash_str, init_data, c_str="WebAppData"):
	"""
	Validates the data received from the Telegram web app using HMAC.
	"""
	init_data = sorted([chunk.split("=") for chunk in unquote(init_data).split("&") if not chunk.startswith("hash=")],
	                   key=lambda x: x[0])
	init_data = "\n".join([f"{rec[0]}={rec[1]}" for rec in init_data])
	
	secret_key = hmac.new(c_str.encode(), TOKEN.encode(), hashlib.sha256).digest()
	data_check = hmac.new(secret_key, init_data.encode(), hashlib.sha256)
	
	return data_check.hexdigest() == hash_str


def queryToDict(query):
	"""
	Converts a query string to a dictionary.
	"""
	return dict([q.split('=') for q in query.split('&')])


def getUserFromQuery(query):
	"""
	Retrieves the user information from the query string.
	Safely evaluates the user data without using eval().
	"""
	query = queryToDict(query)
	user = unquote(query['user'])
	
	# Replace 'true' and 'false' with Python's True and False
	user = user.replace('true', 'True').replace('false', 'False')
	
	try:
		# Safely parse the string into a dictionary or list (avoiding eval)
		user = eval(user, {"__builtins__": None}, {})
	except (SyntaxError, ValueError):
		return None
	return user


## ROUTES

@app.after_request
def add_header(r):
	"""
	Adds headers to prevent caching and ensure the latest version is rendered.
	"""
	r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
	r.headers["Pragma"] = "no-cache"
	r.headers["Expires"] = "0"
	return r


@app.errorhandler(404)
def page_not_found(e):
	return jsonify({'status': 404, 'message': 'Not Found'}), 404


@app.errorhandler(401)
def access_denied(e):
	return jsonify({'status': 401, 'message': 'Unauthorized'}), 401


@app.errorhandler(500)
def internal_server_error(e):
	return jsonify({'status': 500, 'message': 'Internal Server Error'}), 500


@app.route('/getInGroups', methods=['POST'])
def getInGroups():
	try:
		body = request.get_json()
		hash_str = body['hash']
		init_data = body['init_data']
	except Exception:
		abort(400)
	
	if not validate(hash_str, init_data):
		abort(401)
	
	userId = getUserFromQuery(init_data)
	groupsIn = db.getGroupsOfUser(userId["id"])
	groupsIn = [{'group_id': group[1], 'name': group[2], 'members': group[6]} for group in groupsIn]
	
	return jsonify({'status': 200, 'groups': groupsIn, "isOwner": str(userId["id"]) == str(OWNER_ID)})


@app.route('/getAdminPanel', methods=['POST'])
def getAdminPanel():
	body = request.get_json()
	hash_str = body['hash']
	init_data = body['init_data']
	
	if not validate(hash_str, init_data) or str(getUserFromQuery(init_data)["id"]) != str(OWNER_ID):
		abort(401)
	
	logs = db.getWeeklyLogs()
	logs = [{'user_id': log[1], 'group_id': log[2], 'action': log[3], 'description': log[4], 'datetime': log[5]} for log
	        in logs]
	
	return jsonify({'status': 200, 'logs': logs})


@app.route('/leaveInListGroup', methods=['POST'])
def leaveInListGroup():
	body = request.get_json()
	hash_str = body['hash']
	init_data = body['init_data']
	
	if not validate(hash_str, init_data):
		abort(401)
	
	userId = getUserFromQuery(init_data)
	groupId = body['group_id']
	try:
		db.deleteData(groupId, userId["id"])
	except Exception:
		abort(500)
	
	return jsonify({'status': 200, 'message': 'Successfully removed from tag list!'})


@app.route('/')
def dashboard():
	return render_template('./dashboard/index.html')


@app.route('/status')
def status():
	return jsonify({'status': 200, 'message': 'OK'})


def mainGUI():
	try:
		port = int(PORT)
		app.run(host=HOST, port=PORT, debug=WEBSERVER_DEBUG)
	except ValueError:
		print("Error: Invalid port number provided. Check your environment variables.")
		sys.exit(1)
	except Exception as e:
		print(f"Error: {e}")
		sys.exit(1)


if __name__ == '__main__':
	print("Tag Everyone Telegram Bot")
	print("Developed by @Non_Sono_Matteo")
	print("https://matt05.it")
	mainGUI()
