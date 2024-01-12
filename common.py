import git
from git import RemoteProgress
from flask import Flask, jsonify, request
from json.encoder import JSONEncoder
import threading
from flask_socketio import SocketIO, send, emit
from flask_cors import CORS
import os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")