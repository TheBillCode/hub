import time
import couchdb2
import requests
from influxdb import InfluxDBClient
#time.sleep(40)
###  CouchDB ###
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

### InfluxDB ###
#client = InfluxDBClient(host='influxdb', port=8086)
#client.create_database('grow1')

