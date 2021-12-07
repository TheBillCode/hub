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

import json
import requests
import paho.mqtt.client as mqtt
from plantstudiolib import Room 
from plantstudiolib import Plantsudio as ps
import sys, os

#define a list of keywords to populate influx with
KEYWORDS = ["Temperature",
            "Humidity",
            "CarbonDioxide",
            "Power",
            "Weight",
            "Today"]

#http = urllib3.PoolManager()
# Use CouchDB for storing all Studio vars
#ps=CouchDB('http://couchdb:5984/plantstudio')
# Get germinate vars from couchdb
#germinateVars = ps.get('germinate').json()

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

#controls moving to plantstudiolib.py on next release

def controls(msg):
    return
    # this is commmented out because couch db isn't working on my end
    # def fertigate(plant,weight):
    #     f = ps.get('fertigate').json()
    #     if int(plant) == int(f['plantNumber']):
    #         if float(weight) < float(f['lowWeight']):
    #             if int(f['strike']) < int(f['strikeCount']):
    #                 f['strike'] = f['strike'] + 1
    #                 ps.insert(f) 
    #             else:
    #                 client.publish('cmnd/fertigate/Power1', 'on')
    #                 f['fertigateCount'] += 1 
    #                 f['strike'] = 0
    #                 ps.insert(f)   

    # if msg.topic =='tele/gis/SENSOR':
    #     global germinateVars
    #     germinateVars = ps.get('germinate').json()
    #     print(germinateVars['targetTemp'])
    #     client.publish('tele/gis/val', germinateVars['targetTemp'])
    # elif msg.topic =='tele/germinate/SENSOR':
    #     data = decode(msg)
    #     temp = data["DS18B20"]["Temperature"]
    #     if temp < germinateVars['targetTemp']:
    #         client.publish('cmnd/heatmat/Power1', 'on')
    #     elif temp > germinateVars['targetTemp']:
    #         client.publish('cmnd/heatmat/Power1', 'off') 
    # elif re.search('tele/plant./SENSOR', msg.topic):
    #     data = decode(msg)
    #     weight = data["HX711"]["Weight"]
    #     plant = re.search(r'\d+', msg.topic).group()
    #     #if weight > 0 and weight < 120:
    #     payload = "sensors,type=air Plant" + str(plant) + "Weight=" + str(weight)
    #     InfluxResponse = requests.request("POST", InfluxUrl, data=payload, params=InfluxQueryString)
    #     fertigate(plant,weight)      


def on_message(client, userdata, msg):

    def decode_topic(topic):
        topic = topic[1:-1] #remove tele and SENSOR/STATE
        """Returns room, device, and device name

        Args:
            topic (list): list of topic information

        Returns:
            data: dictionary (room, device, name)
        """
        data = {"room":"", "device":"", "name":""}
        def is_int(x):
            try:
                int(x)
                return True
            except:
                return False
        #-----get name-----       
        if is_int(topic[-1]):
            #get name and number
            data["name"] = topic[-2] + topic[-1]
            del topic[-2:] #remove name/number from topic
        else:
            data["name"] = topic[-1]
            topic.pop()
        #-----get device-----
        data["device"] = topic.pop()
        #-----get room-----
        if len(topic) > 1 and topic[0].lower() == "ps":
            topic.pop(0) #remove 'ps' from room name
            data["room"] = "-".join(topic)
        else:
            data["room"] = "ps"
        return (data)
       
    if "SENSOR" not in msg.topic and "STATE" not in msg.topic:
        return
    
    try:
        pairs = dict()
        topic = decode_topic(msg.topic.split("/")) #ps/flower/s31/light/1      
        if not Room.known_room(topic["room"]):
            Room(topic["room"])
        
        #set topic for influxdb and grafana
        payload = topic["room"] + ",name=" + topic["name"] + "(" + topic["device"] + ") "
        data = decode(msg)
        pairs = ps.get_keywords(data)
        if pairs:
            Room.update_room(topic["room"], pairs)

        #add sensor parameters to payload
        for k in pairs:
            payload += k + "=" + str(pairs[k]) + ","
        payload = payload[:-1]
        InfluxResponse = requests.request("POST", InfluxUrl, data=payload, params=InfluxQueryString)
    except Exception as e: 
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)



def on_message(client, userdata, msg):
    if "LWT" in msg.topic:
        return
    def get_keywords(data):
        """Returns all key-value pairs where key is a KEYWORD using
        recursion to iterate through all dictionaries in dictionoary
        """
        pairs = {}
        for k,v in data.items():        
            if isinstance(v, dict):
                pairs = get_keywords(v)
            else:   
                if k in KEYWORDS:
                    pairs[k] = v
        return pairs         
  
    if "SENSOR" in msg.topic:
        try:
            pairs = dict()
            topic = msg.topic.split("/") #tele/Device/Type
            payload = topic[1] + ",type=" + topic[2] + " " #set topics
            data = decode(msg)
            pairs = get_keywords(data) 
            
            for k in pairs:
                payload += k + "=" + str(pairs[k]) + ","
            payload = payload[:-1]
            InfluxResponse = requests.request("POST", InfluxUrl, data=payload, params=InfluxQueryString)
        except Exception as e: print(e)
    #uncomment if using controls
    #controls(msg)

    


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("mosquitto", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.

client.loop_forever()