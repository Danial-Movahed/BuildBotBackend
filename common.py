import git
from git import RemoteProgress
from flask import Flask, jsonify, request
from json.encoder import JSONEncoder
import threading
import multiprocessing
from flask_socketio import SocketIO, send, emit
from flask_cors import CORS
import os
import psutil
from time import sleep
import json
import subprocess

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
buildingProcess = None
buildCMD = "/usr/bin/env make"