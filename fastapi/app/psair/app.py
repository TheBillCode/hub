 # 
 # This file is part of the PlantStudio Hub distribution (https://github.com/plant-studio/hub).
 # Copyright (c) 2015 Simon Romanski.
 # 
 # This program is free software: you can redistribute it and/or modify  
 # it under the terms of the GNU General Public License as published by  
 # the Free Software Foundation, version 3.
 #
 # This program is distributed in the hope that it will be useful, but 
 # WITHOUT ANY WARRANTY; without even the implied warranty of 
 # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU 
 # General Public License for more details.
 #
 # You should have received a copy of the GNU General Public License 
 # along with this program. If not, see <http://www.gnu.org/licenses/>.
 #
import os
import sys
import requests
import time
import json
import serial
import AM2315
import RPi.GPIO as GPIO
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify
from pyduino import *
from crontab import CronTab
from flask_cors import CORS
from time2relax import CouchDB
from flask_mqtt import Mqtt

# **************************
# THIS IS THE AIR CONTROLLER
# **************************

app = Flask(__name__)
CORS(app)
#couchserver = couchdb.Server("http://couchdb:5984/")
#db = couchserver['gp']
ps=CouchDB('http://couchdb:5984/plantstudio')


# InfluxDb
InfluxUrl = "http://influxdb:8086/write"
InfluxQueryString = {"db": "grow1", "precision": "ms"}
 

# SETUP GPIO mode and initiat used pins
GPIO.setmode(GPIO.BCM)
outPins = [19,26]
GPIO.setup(outPins, GPIO.OUT)

# START SENSIBO ################
sensibo = {'url':'https://home.sensibo.com/api/v2','apiKey':'[API-KEY]','deviceId':'[DEVICE-ID]'}
# END SENSIBO ##################

# START CO2 SENSOR #############
ser = serial.Serial("/dev/serial0")
ser.write(str.encode("K 2\r\n"))
ser.flushInput()
# END CO2 SENSOR ###############

# START AIR TEMP/HUMIDITY SENSOR #######
sensor = AM2315.AM2315()
# END AIR TEMP/HUMIDITY SENSOR #########

# Start MQTT ##############
app.config['MQTT_BROKER_URL'] = 'mosquitto'
app.config['MQTT_BROKER_PORT'] = 1883
#app.config['MQTT_USERNAME'] = 'user'
#app.config['MQTT_PASSWORD'] = 'secret'
app.config['MQTT_REFRESH_TIME'] = 1.0  # refresh time in seconds
mqtt = Mqtt(app)
# End MQTT ################

#mqtt.subscribe('#')

#@mqtt.on_message()
#def handle_mqtt_message(client, userdata, message):
#  data = dict(
#    topic=message.topic,
#    payload=message.payload.decode()
#    )
# print (data['topic'])

@app.route("/mqtt/<device>/<message>")
def mq(device, message):
  mqtt.publish('cmnd/' + device + '/Power1', message)
  return 'toggle fan'

@app.route("/cmnd/<device>/<topic>/<message>")
def cmnd(device,topic,message):
  mqtt.publish('cmnd/' + device + '/' + topic, message)
  return 'cmnd command successful'

@app.route("/")
def index():
  return 'Plant Studio Air Controller: API'

@app.route('/pin/<pin>/<state>')
def ledon(pin,state):
  GPIO.output(int(pin),int(state))
  return 'Pin ' + pin + ' set to ' + state

@app.route('/readPin/<pin>')
def readPin(pin):
  tickle = GPIO.input(int(pin))
  return str(tickle)

@app.route("/res/fill", methods = ['GET'])
def fillres():
  a.digital_write(8,1)
  a.digital_write(7,0)
  return 'done'

@app.route("/res/liter", methods = ['GET'])
def liter():
  a.digital_write(7,0)
  time.sleep(5)
  a.digital_write(7,1)
  return depth()

@app.route("/res/drain", methods = ['GET'])
def drainres():
  a.digital_write(7,1)
  a.digital_write(8,0)
  return 'done'

@app.route("/res/stop", methods = ['GET'])
def stopres():
  a.digital_write(8,1)
  a.digital_write(7,1)
  return 'done'

@app.route("/light", methods = ['POST','GET'])
def light():
  lightData = ps.get('light').json()
  if request.method == 'POST':
    cron = CronTab(user='root')
    cron.remove_all(comment='sunrise')
    cron.remove_all(comment='sunset')
    cron.write()
    sunrise = cron.new(command='/blah/sunrise.py', comment='sunrise')
    sunrise.setall('0 ' + request.form['sunrise'] + ' * * *')
    lightData['sunrise'] = request.form['sunrise']
    sunset = cron.new(command='/blah/sunset.py', comment='sunset')
    sunset.setall('0 ' + request.form['sunset'] + ' * * *')
    lightData['sunset'] = request.form['sunset']
    cron.write()
    #db.save(lightData)
    ps.insert(lightData)
  return render_template('light.html', light=lightData)

@app.route("/light/<state>", methods = ['GET'])
def lightstate(state):
  lightData = ps.get('light').json()
  if state == 'on':
    mqtt.publish('cmnd/light2/Power1', 'on')
    mqtt.publish('cmnd/light1/Power1', 'on')
    lightData['state'] = 'on'
    ps.insert(lightData)
  elif state == 'off':
    mqtt.publish('cmnd/light2/Power1', 'off')
    mqtt.publish('cmnd/light1/Power1', 'off')
    lightData['state'] = 'off'
    ps.insert(lightData)
  return ('Light ' + state)

@app.route("/dose/pump/<pump>/<ml>", methods = ['GET'])
def dose(pump,ml):
  dose = ps.get('dose').json()
  whichPump = 'pump' + str(pump)
  pump1calibrate = dose['pumps'][whichPump]['calibrate']
  dosetime = round(float(pump1calibrate) * float(ml))
  backgroundDose.delay(pump, dosetime)
  return 'done'

@app.route("/depth", methods=['GET'])
def depth():
  depthReading = float(a.analog_read(0))
  depthReading = (1023 / depthReading) - 1
  depthReading = 560 / depthReading
  d = {'depthReading':depthReading}
  return jsonify(d)

@app.route("/outlet", methods =['GET'])
def outlet():
  backgroundOutlet.delay()
  return 'done'

@app.route("/co2", methods=['GET'])
def co2():
  co2Read = 0
  co2 = 0
  for x in range(0,4):
    ser.write(str.encode("Z\r\n"))
    time.sleep(.1)
    resp = ser.read(10)
    resp = resp[:8]
    if x > 0:
      fltCo2 = float(resp[2:])
      print (fltCo2)
      co2Read = co2Read + fltCo2
      time.sleep(.1)
  co2 = int((co2Read-2)/3)
  value = {'value':co2}
  return json.dumps(value)

@app.route("/airTemp")
def airTemp():
  value = {'value':sensor.read_temperature()}
  return json.dumps(value)

@app.route("/airHumidity")
def airHumidity():
  value = {'value':sensor.read_humidity()}
  return json.dumps(value)


@app.route("/climate/temp")
def climate():
  return str(device.room_temp)

@app.route("/minisplit/power/<state>")
def minipower(state):
  urlString = sensibo['url'] + '/pods/' + sensibo['deviceId'] + '/acStates' + '/?apiKey=' + sensibo['apiKey']
  if state == 'on':
    r = requests.post(urlString, data='{"acState":{"on":true}}')
  elif state == 'off':
    r = requests.post(urlString, data='{"acState":{"on":false}}')
  return 'power state set to ' + state

@app.route("/minisplit/mode/<request>")
def minisplit(request):
  if request == 'cool':
    device.cool.activate()
  elif request == 'fan':
    device.fan.activate()
#  else:
#    device.auto.activate()
  return 'Minisplit set to ' + request

@app.route("/minisplit/temp/<temp>")
def minitemp(temp):
  urlString = sensibo['url'] + '/pods/' + sensibo['deviceId'] + '/acStates/targetTemperature' + '?apiKey=' + sensibo['apiKey']
  tempString = '{"newValue":' + str(temp) +'}'
  r = requests.patch(urlString, data= tempString)  
  return 'set temp to ' + temp

@app.route("/minisplit/fan/<mode>")
def minifan(mode):
  urlString = sensibo['url'] + '/pods/' + sensibo['deviceId'] + '/acStates/fanLevel' + '?apiKey=' + sensibo['apiKey']
  fanString = '{"newValue":' + '"' + mode +'"}'
  r = requests.patch(urlString, data= fanString)
  return 'fan mode set to ' + mode

@app.route("/minisplit/swing/<mode>")
def miniswing(mode):
  urlString = sensibo['url'] + '/pods/' + sensibo['deviceId'] + '/acStates/swing' + '?apiKey=' + sensibo['apiKey']
  swingString = '{"newValue":' + '"' + mode +'"}'
  r = requests.patch(urlString, data= swingString)  
  return 'swing set to ' + mode

@app.route("/logStudio", methods = ['GET'])
def logStudio():
  f = open("studioVars.json", "r")
  studioVars = json.loads(f.read())
  getTemp = airTemp()
  tempJson = json.loads(getTemp)
  studioTemp = tempJson['value']
  getHumidity = airHumidity()
  tempJson = json.loads(getHumidity)
  humidity = tempJson['value']
  getCo2 = co2()
  tempJson = json.loads(getCo2)
  CO2 = tempJson['value']
  lightData = ps.get('light').json()
  updatedAt = datetime.now().isoformat()
  # Post to Influx
  payload = "sensors,type=air StudioTemp=" + str(studioTemp) + ",StudioHumidity=" + str(humidity) + ",StudioCO2=" + str(CO2)
  InfluxResponse = requests.request("POST", InfluxUrl, data=payload, params=InfluxQueryString)
  if humidity > int(studioVars['humidityHigh']):
    mqtt.publish('cmnd/humidifier/Power1', 'off')
  elif humidity < int(studioVars['humidityLow']):
    mqtt.publish('cmnd/humidifier/Power1', 'on')
  #if humidity > int(studioVars['dehumidifierOn']):
  #  mqtt.publish('cmnd/dehumidifier/Power1', 'on')
  #elif humidity < int(studioVars['dehumidifierOff']):
  #  mqtt.publish('cmnd/dehumidifier/Power1', 'off')
  if studioTemp > int(studioVars['heaterHigh']):
    mqtt.publish('cmnd/heater/Power1', 'off')
  elif studioTemp < int(studioVars['heaterLow']):
    mqtt.publish('cmnd/heater/Power1', 'on')
  #if studioTemp > float(studioVars['acOn']):
  #  minipower('on')
  if CO2 > int(studioVars['co2High']):
    mqtt.publish('cmnd/co2/Power2','off')
  elif CO2 < int(studioVars['co2Low']) and lightData['state'] == 'on':
    mqtt.publish('cmnd/co2/Power2', 'on')
  return 'done'

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=88, debug=True)
