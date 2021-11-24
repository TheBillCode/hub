import time
import couchdb2
import requests
from influxdb import InfluxDBClient
from flask import Flask
from flask import render_template
import subprocess

app = Flask(__name__)

def run_command(command):
    subprocess.call('/code/app/' + command + '.sh')
    return('SENT')

@app.route("/")
def hello_world():
    return render_template('index.html')

@app.route('/sh/<command>')
def command_server(command):
    return run_command(command)

@app.route('/couchdb')
def couch_init():
    server = couchdb2.Server(href="http://couchdb:5984/", username="admin", password="password", use_session=True, ca_file=None)
    db = server.create("plantstudio")
    db = server["plantstudio"]
    studioVars = {
        "_id": "studioVars",
        "humidityHigh": "65",
        "humidityLow": "60",
        "heaterHigh": "22",
        "heaterLow": "22",
        "acOn": "27"
        }
    db.put(studioVars)

    germinate = {
        "_id": "germinate",
        "heatSource": "heatmat",
        "targetTemp": 17
    }
    db.put(germinate)

    light = {
        "_id": "light",
        "state": "on",
        "type": "Fluence SpydrX Plus"
    }
    db.put(light)
    return('Configure Counchdb')