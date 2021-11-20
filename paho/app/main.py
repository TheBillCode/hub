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
import json
#import urllib3
import requests
import re
from time2relax import CouchDB
import paho.mqtt.client as mqtt

#http = urllib3.PoolManager()
# Use CouchDB for storing all Studio vars
ps=CouchDB('http://couchdb:5984/plantstudio')
# Get germinate vars from couchdb
germinateVars = ps.get('germinate').json()

# InfluxDb config
InfluxUrl = "http://influxdb:8086/write"
InfluxQueryString = {"db": "grow1", "precision": "ms"}

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

# Subscribing in on_connect() means that if we lose the connection and
# reconnect then subscriptions will be renewed.
    client.subscribe("tele/#")
# The callback for when a PUBLISH message is received from the server.

def decode(message):
    m = (message.payload.decode("utf-8"))
    data = json.loads(m)
    return data

def fertigate(plant,weight):
    f = ps.get('fertigate').json()
    if int(plant) == int(f['plantNumber']):
        if float(weight) < float(f['lowWeight']):
            if int(f['strike']) < int(f['strikeCount']):
                f['strike'] = f['strike'] + 1
                ps.insert(f) 
            else:
                client.publish('cmnd/fertigate/Power1', 'on')
                f['fertigateCount'] += 1 
                f['strike'] = 0
                ps.insert(f)   
    return "done"

def on_message(client, userdata, msg):
#    m = (msg.payload.decode("utf-8"))
#    data = json.loads(m)
    print('message')
    if msg.topic =='tele/esp4/SENSOR':
        data = decode(msg)
        temp = data["AM2301"]["Temperature"]
        humid = data["AM2301"]["Humidity"]
        payload = "sensors,type=air OutsideTemp=" + str(temp) + ",OutsideHumidity=" + str(humid)
        InfluxResponse = requests.request("POST", InfluxUrl, data=payload, params=InfluxQueryString)
    elif msg.topic == 'tele/mist/duration':
        payload = "sensors,type=air MistDuration=" + str(decode(msg))
        InfluxResponse = requests.request("POST", InfluxUrl, data=payload, params=InfluxQueryString)
    elif msg.topic =='tele/seedling/SENSOR':
        data = decode(msg)
        temp = data["AM2301"]["Temperature"]
        humid = data["AM2301"]["Humidity"]
        payload = "sensors,type=air curingTemp2=" + str(temp) + ",curingHumidity2=" + str(humid)
        InfluxResponse = requests.request("POST", InfluxUrl, data=payload, params=InfluxQueryString)
    elif msg.topic =='tele/bme280_1/SENSOR':
        data = decode(msg)
        temp = data["BME280"]["Temperature"]
        humid = data["BME280"]["Humidity"]
        humid = humid + 10 #compensate for low reading
        payload = "sensors,type=air BME1Temp=" + str(temp) + ",BME1Humidity=" + str(humid)
        InfluxResponse = requests.request("POST", InfluxUrl, data=payload, params=InfluxQueryString)     
    elif msg.topic =='tele/heater/SENSOR':
        data = decode(msg)
        watts = data["ENERGY"]["Power"]
        payload = "sensors,type=air HeaterWatts=" + str(watts)
        InfluxResponse = requests.request("POST", InfluxUrl, data=payload, params=InfluxQueryString)
    elif msg.topic =='tele/humidifier/SENSOR':
        data = decode(msg)
        watts = data["ENERGY"]["Power"]
        payload = "sensors,type=air HumidifierWatts=" + str(watts)
        InfluxResponse = requests.request("POST", InfluxUrl, data=payload, params=InfluxQueryString)    
    elif msg.topic =='tele/gis/SENSOR':
        global germinateVars
        germinateVars = ps.get('germinate').json()
        print(germinateVars['targetTemp'])
        client.publish('tele/gis/val', germinateVars['targetTemp'])
    elif msg.topic =='tele/germinate/SENSOR':
        data = decode(msg)
        temp = data["DS18B20"]["Temperature"]
        if temp < germinateVars['targetTemp']:
            client.publish('cmnd/heatmat/Power1', 'on')
        elif temp > germinateVars['targetTemp']:
            client.publish('cmnd/heatmat/Power1', 'off') 
        payload = "sensors,type=air GroundTemp=" + str(temp)
        InfluxResponse = requests.request("POST", InfluxUrl, data=payload, params=InfluxQueryString)
    elif msg.topic =='tele/garage/SENSOR':
        data = decode(msg)
        temp = data["SHT3X-0x45"]["Temperature"]
        humidity = data["SHT3X-0x45"]["Humidity"]
        payload = "sensors,type=air curingTemp=" + str(temp) + ",curingHumidity=" + str(humidity)
        InfluxResponse = requests.request("POST", InfluxUrl, data=payload, params=InfluxQueryString)
    elif msg.topic =='tele/light1/SENSOR':
        data = decode(msg)
        watts = data["ENERGY"]["Power"]
        payload = "sensors,type=air Light1Watts=" + str(watts)
        InfluxResponse = requests.request("POST", InfluxUrl, data=payload, params=InfluxQueryString)
    elif msg.topic =='tele/heatmat/SENSOR':
        data = decode(msg)
        watts = data["ENERGY"]["Power"]
    elif msg.topic =='tele/light2/SENSOR':
        data = decode(msg)
        watts = data["ENERGY"]["Power"]
        payload = "sensors,type=air Light2Watts=" + str(watts)
        InfluxResponse = requests.request("POST", InfluxUrl, data=payload, params=InfluxQueryString)
    elif msg.topic =='tele/fan/SENSOR':
        data = decode(msg)
        watts = data["ENERGY"]["Power"]
        payload = "sensors,type=air FanWatts=" + str(watts)
        InfluxResponse = requests.request("POST", InfluxUrl, data=payload, params=InfluxQueryString)
    elif msg.topic =='tele/hyperfan/SENSOR':
        data = decode(msg)
        watts = data["ENERGY"]["Power"]
        payload = "sensors,type=air HyperfanWatts=" + str(watts)
        InfluxResponse = requests.request("POST", InfluxUrl, data=payload, params=InfluxQueryString)
    elif msg.topic =='tele/dehumidifier/SENSOR':
        data = decode(msg)
        watts = data["ENERGY"]["Power"]
        wattsToday = data["ENERGY"]["Today"]
        payload = "sensors,type=air DehumidifierWatts=" + str(watts) + ",DehumidifierWattsToday=" + str(wattsToday)
        InfluxResponse = requests.request("POST", InfluxUrl, data=payload, params=InfluxQueryString)
    elif msg.topic =='tele/co2/SENSOR':
        data = decode(msg)
        watts = data["ENERGY"]["Power"]
        payload = "sensors,type=air CO2Watts=" + str(watts)
        InfluxResponse = requests.request("POST", InfluxUrl, data=payload, params=InfluxQueryString)
    elif msg.topic =='tele/roflood/SENSOR':
        data = decode(msg)
        counter = data["COUNTER"]["C1"]
    elif re.search('tele/plant./SENSOR', msg.topic):
        data = decode(msg)
        weight = data["HX711"]["Weight"]
        plant = re.search(r'\d+', msg.topic).group()
#        if weight > 0 and weight < 120:
        payload = "sensors,type=air Plant" + str(plant) + "Weight=" + str(weight)
        InfluxResponse = requests.request("POST", InfluxUrl, data=payload, params=InfluxQueryString)
        fertigate(plant,weight)   
#    elif msg.topic == 'tele/seedling/ALERT':
#        r = http.request('GET', 'http://10.0.0.0:88/minisplit/power/on')
#       result = r.status
#       client.publish('cmnd/seedling/Rule1', 'off')

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("mosquitto", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.

client.loop_forever()
