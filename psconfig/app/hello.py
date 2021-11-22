from flask import Flask
import subprocess

app = Flask(__name__)


def run_command():
    subprocess.call('/code/app/app/test.sh')
    return('SENT')

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route('/stop')
def command_server():
    return run_command()    
